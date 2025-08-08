import os

from py2docfx.convert_prepare.params import load_file_params, load_command_params


def extract_package_infos(iterator):
    return [package_info for package_info in iterator[0]], [
        required_package_info for required_package_info in iterator[1]
    ]


def package_info_assert(package_info_list, required_package_info_list):
    package = package_info_list[0]
    assert package.name == "azure-mltable-py2docfxtest"
    assert package.install_type.name == "PYPI"
    assert package.exclude_path == ["test*", "example*", "sample*", "doc*"]

    package = package_info_list[1]
    assert package.name == "azureml-accel-models"
    assert package.install_type.name == "PYPI"
    assert package.exclude_path == []

    package = package_info_list[3]
    assert package.name == "semantic-kernel"
    assert package.install_type.name == "PYPI"
    assert package.sphinx_extensions == ["sphinx-pydantic"]

    required_package = required_package_info_list[0]
    assert required_package.name == None
    assert required_package.install_type.name == "DIST_FILE"
    assert required_package.location == "https://dummy/dummy.py3-none-any.whl"

    required_package = required_package_info_list[1]
    assert required_package.name == "jinja2"
    assert required_package.install_type.name == "PYPI"
    assert required_package.version == "<3.1.0"


def test_load_command_params():
    # read test json
    json_str = ""
    with open("convert_prepare/tests/data/params/test.json", "r") as f:
        json_str = f.read()

    json_info = load_command_params(json_str)

    package_info_list, required_package_info_list = extract_package_infos(json_info)

    package_info_assert(package_info_list, required_package_info_list)


def test_load_file_params():
    # get absolute path of test json
    path = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join("data", "params", "test.json")
    full_path = os.path.join(path, relative_path)
    json_info = load_file_params(full_path)

    package_info_list, required_package_info_list = extract_package_infos(json_info)

    package_info_assert(package_info_list, required_package_info_list)
