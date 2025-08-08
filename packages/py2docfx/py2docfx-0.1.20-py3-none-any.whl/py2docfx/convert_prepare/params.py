import json
from py2docfx.convert_prepare.package_info import PackageInfo


def load_command_params(param_json):
    """
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/common/common.ps1&version=GBmaster&line=552&lineEnd=553&lineStartColumn=1&lineEndColumn=1&lineStyle=plain&_a=contents
    Load params from command Json

    :return: deserialized param json as dict, transform the packages to PackageInfo
    """

    params = json.loads(param_json)
    package_info_list = params.get("packages", [])
    required_packages = params.get("required_packages", [])
    return (
        _load_package_infos(package_info_list),
        _load_package_infos(required_packages, reading_required_packages=True),
    )


def load_file_params(file_path):
    """
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/common/common.ps1&version=GBmaster&line=556&lineEnd=557&lineStartColumn=1&lineEndColumn=1&lineStyle=plain&_a=contents
    Load params from a local file (usually in repo)

    :return: deserialized param json as dict, transform the packages to PackageInfo
    """
    with open(file_path, "r", encoding="utf-8") as file:
        params = json.load(file)
        package_info_list = params.get("packages", [])
        required_packages = params.get("required_packages", [])
        return (
            _load_package_infos(package_info_list),
            _load_package_infos(required_packages, reading_required_packages=True),
        )


def _load_package_infos(
    package_info_list, reading_required_packages=False
) -> list[PackageInfo]:
    for package_info in package_info_list:
        yield PackageInfo.parse_from(package_info, reading_required_packages)
