import asyncio
import os
import subprocess
import sys

from py2docfx import PACKAGE_ROOT
from py2docfx.docfx_yaml.logger import get_package_logger,run_async_subprocess
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.paths import folder_is_hidden
from py2docfx.convert_prepare.subpackage import (get_subpackages,
                                        move_rst_files_to_subfolder)

DEBUG_SPHINX_FLAG = 'PY2DOCFX_DEBUG_SPHINX'

async def run_apidoc(package_name, rst_path, source_code_path, exclude_paths, package_info: PackageInfo):
    """
    Run sphinx-apidoc to generate RST inside rst_path folder

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/build.ps1&line=110&lineEnd=126&lineStartColumn=1&lineEndColumn=14&lineStyle=plain&_a=contents
    """
    py2docfx_logger = get_package_logger(__name__, package_name)
    subfolderList = [name for name in
                       os.listdir(source_code_path)
                       if os.path.isdir(os.path.join(source_code_path, name))
                       and not folder_is_hidden(os.path.join(source_code_path, name))]
    package_paths = package_info.path
    subpackages_rst_record = None
    for subfolder in subfolderList:
        subfolderPath = os.path.join(source_code_path, subfolder)
        if os.path.isdir(subfolderPath):
            msg = "<CI INFO>: Subfolder path {}.".format(subfolderPath)
            py2docfx_logger.info(msg)
            args = [
                "--module-first",
                "--no-headings",
                "--no-toc",
                "--implicit-namespaces",
                "-o",
                rst_path,
                subfolderPath,
            ]
            args.extend(exclude_paths)
            full_args = ["-m", "sphinx.ext.apidoc"] + args
            await run_async_subprocess(sys.executable, full_args, py2docfx_logger)
            if package_info.build_in_subpackage and subfolder == "azure":
                subpackages_rst_record = move_rst_files_to_subfolder(
                    package_paths.doc_folder, package_info.name,
                    get_subpackages(subfolderPath, package_info.name))
    return subpackages_rst_record


async def run_converter(package_name: str,
                    rst_path,
                    out_path,
                    sphinx_build_path: str,
                    extra_package_path: str,
                    conf_path = None,
                    executable = sys.executable):
    """
    Take rst files as input and run sphinx converter

    :return: the location of generated yamls

    Replacing
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/build.ps1&line=150&lineEnd=161&lineStartColumn=13&lineEndColumn=52&lineStyle=plain&_a=contents
    """
    py2docfx_logger = get_package_logger(__name__, package_name)
    outdir = os.path.join(out_path, "_build")

    # Sphinx/docutils have memory leak including linecaches, module-import-caches,
    # Use a subprocess on production to prevent out of memory

    if not sys.executable:
        msg = "Can't get the executable binary for the Python interpreter."
        py2docfx_logger.error(msg)
        raise ValueError(msg)
    sphinx_param = [
        sphinx_build_path,
        rst_path,
        outdir,
        '-c', conf_path or rst_path,
        '-d', os.path.join(outdir, "doctrees"),
        '-b', 'yaml'
    ]

    # TODO: update generate_conf to replace "yaml_builder" with "py2docfx.docfx_yaml.yaml_builder"
    # then no need to manually add docfx_yaml to path
    package_root_parent = os.path.join(PACKAGE_ROOT, 'docfx_yaml')
    os.environ['PROCESSING_PACKAGE_NAME'] = package_name
    env_tmp = os.environ.copy()
    if os.name == 'nt' : # TODO: may need to add basevenv site-packages if not work
        env_tmp["PYTHONPATH"] = f"{extra_package_path};{package_root_parent};"
    else:
        env_tmp["PYTHONPATH"] = f"{extra_package_path}:{package_root_parent}:"
    proc = await asyncio.create_subprocess_exec(
        executable, *sphinx_param,
        cwd=PACKAGE_ROOT,
        env=env_tmp,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    return_code = proc.returncode

    if return_code == 0:
        py2docfx_logger.info(f"{stdout}")
        py2docfx_logger.info(f"{stderr}")
    else:
        py2docfx_logger.error(f"{stderr}")
        raise subprocess.CalledProcessError(return_code, sphinx_param, stdout, stderr)

    return outdir
