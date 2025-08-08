import argparse
import logging
import os

from py2docfx.convert_prepare.params import load_file_params, load_command_params
from py2docfx.convert_prepare.package_info import PackageInfo

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            """A command line tool to run Sphinx with docfx-yaml extension, 
                        transform python source code packages to yamls supported in docfx"""
        )
    )

    parser.add_argument(
        "-o"
        "--output-root-folder",
        default=None,
        dest="output_root",
        help="The output folder storing generated documents, use cwd if not assigned",
    )
    parser.add_argument(
        "--github-token",
        default=None,
        dest="github_token",
        help="Allow pipeline to clone Github source code repo",
    )
    parser.add_argument(
        "--ado-token",
        default=None,
        dest="ado_token",
        help="Allow pipeline to clone Azure DevOps source code repo",
    )
    parser.add_argument(
        "-f",
        "--param-file-path",
        dest="param_file_path",
        help="The json file contains package infomation",
    )
    parser.add_argument(
        "-j",
        "--param-json",
        default=None,
        dest="param_json",
        help="The json string contains package infomation",
    )
    parser.add_argument(
        "-t",
        "--install-type",
        action="store",
        dest="install_type",
        choices=["pypi", "source_code", "dist_file"],
        help="""The type of source package, can be pip package, github repo or a distribution
                        file accessible in public""",
    )
    parser.add_argument(
        "-n",
        "--package-name",
        default=None,
        dest="package_name",
        help="The name of source package, required if INSTALL_TYPE==pypi",
    )
    parser.add_argument(
        "-v",
        "--version",
        default=None,
        dest="version",
        help="The version of source package, if not assigned, will use latest version",
    )
    parser.add_argument(
        "-i",
        "--extra-index-url",
        default=None,
        dest="extra_index_url",
        help="Extra index of pip to download source package",
    )
    parser.add_argument(
        "--url",
        default=None,
        dest="url",
        help="""Valid when INSTALL_TYPE==source_code, url of the repo to
                        clone which contains SDK package source code.""",
    )
    parser.add_argument(
        "--branch",
        default=None,
        dest="branch",
        help="""Valid when INSTALL_TYPE==source_code, branch of the repo to clone which
                        contains SDK package source code.""",
    )
    parser.add_argument(
        "--editable",
        default=False,
        dest="editable",
        help="""Install a project in editable mode.""",
    )
    parser.add_argument(
        "--folder",
        default=None,
        dest="folder",
        help="""Valid when INSTALL_TYPE==source_code, relative folder path inside the repo
                        containing SDK package source code.""",
    )
    parser.add_argument(
        "--prefer-source-distribution",
        dest="prefer_source_distribution",
        action="store_true",
        help="""Valid when INSTALL_TYPE==pypi, a flag which add --prefer-binary
                        option to pip commands when getting package source.""",
    )
    parser.add_argument(
        "--location",
        default=None,
        dest="location",
        help="""Valid when INSTALL_TYPE==dist_file, the url of distribution file
                        containing source package.""",
    )
    parser.add_argument(
        "--build-in-subpackage",
        action="store_true",
        dest="build_in_subpackage",
        help="""When package has lot of big subpackages and each doesn't depend on others
                    enable to fasten build""",
    )
    parser.add_argument(
        "exclude_path",
        default=[],
        nargs="*",
        help="""A list containing relative paths to the root of the package of files/directories
                        excluded when generating documents, should follow fnmatch-style.""",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="""Increase output verbosity. Cannot be used together with --show-warning""",
    )
    
    parser.add_argument(
        "--show-warning",
        action="store_true",
        help="""Show warning message. Cannot be used together with --verbose""",
    )
    return parser


def parse_command_line_args(argv) -> (
        list[PackageInfo], list[PackageInfo], str, str, str | os.PathLike, bool, bool):
    parser = get_parser()
    args = parser.parse_args(argv)

    github_token = args.github_token
    ado_token = args.ado_token
    output_root = args.output_root
    verbose = args.verbose
    show_warning = args.show_warning

    if args.param_file_path:
        (package_info_list, required_packages) = load_file_params(args.param_file_path)
        return (list(package_info_list), list(required_packages), github_token,
                ado_token, output_root, verbose, show_warning)
    elif args.param_json:
        (package_info_list, required_packages) = load_command_params(args.param_json)
        return (list(package_info_list), list(required_packages), github_token,
                ado_token, output_root, verbose, show_warning)
    else:
        package_info = PackageInfo()
        if not args.install_type:
            PackageInfo.report_error("install_type", args.install_type)
        package_info.install_type = PackageInfo.InstallType[
            args.install_type.upper()
        ]

        package_info.name = args.package_name
        package_info.version = args.version
        package_info.extra_index_url = args.extra_index_url
        package_info.editable = args.editable
        package_info.prefer_source_distribution = (
            args.prefer_source_distribution
        )
        package_info.build_in_subpackage = args.build_in_subpackage
        package_info.exclude_path = args.exclude_path

        if (
            package_info.install_type == PackageInfo.InstallType.PYPI
            and not package_info.name
        ):
            PackageInfo.report_error("name", "None")

        if package_info.install_type == PackageInfo.InstallType.SOURCE_CODE:
            package_info.url = args.url
            package_info.branch = args.branch
            package_info.folder = args.folder
            if not package_info.url:
                if not package_info.folder:
                    msg = "When install_type is source_code, folder or url should be provided"
                    raise ValueError(msg)
                else:
                    msg = f"Read source code from local folder: {package_info.folder}"
                    logging.info(msg)

        if package_info.install_type == PackageInfo.InstallType.DIST_FILE:
            package_info.location = args.location
            if not package_info.location:
                PackageInfo.report_error(
                    "location",
                    "None",
                    condition="When install_type is dist_file",
                )
        return ([package_info], [], github_token, ado_token, output_root, verbose, show_warning)