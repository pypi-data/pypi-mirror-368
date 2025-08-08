import os
import json

from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.source import Source

test_dict = dict()
param_case_dir = "convert_prepare/tests/data/params/"
full_test_file_path = os.path.join(param_case_dir, "test.json")

with open(full_test_file_path, "r", encoding="utf-8") as json_file:
    test_dict = json.load(json_file)
package_info_0 = PackageInfo.parse_from(test_dict["packages"][0], False)
package_info_0.code_location = "dummy_location"

package_info_1 = PackageInfo.parse_from(test_dict["packages"][1], False)

package_info_2 = PackageInfo.parse_from(test_dict["packages"][2], False)

package_info_3 = PackageInfo.parse_from(test_dict["packages"][3], False)

def test_parse_from():
    assert package_info_0.exclude_path == ["test*", "example*", "sample*", "doc*"]
    assert package_info_0.name == "azure-mltable-py2docfxtest"
    assert package_info_0.install_type.name == "PYPI"

def test_get_combined_name_version():
    name_version = package_info_1.get_combined_name_version()
    assert name_version == "azureml-accel-models==1.0.0"

def test_get_sphinx_extensions():
    assert package_info_3.sphinx_extensions == ["sphinx-pydantic"]
    assert package_info_3.name == "semantic-kernel"
    assert package_info_3.install_type.name == "PYPI"

def test_intall_command():
    install_command = package_info_0.get_install_command()
    assert install_command[0] == "azure-mltable-py2docfxtest"
    assert install_command[1] == ["--upgrade"]

    install_command = package_info_1.get_install_command()
    assert install_command[0] == "azureml-accel-models==1.0.0"
    assert install_command[1] == []

def test_get_exclude_command(tmp_path):
    source_folder = os.path.join(tmp_path,"source_folder")
    yaml_output_folder = os.path.join(tmp_path,"yaml_output_folder")
    package_info_0.path = Source(
        source_folder = source_folder, yaml_output_folder = yaml_output_folder, package_name = "azure-mltable-py2docfxtest"
    )
    exclude_path = package_info_0.get_exluded_command()
    expected_exclude_path = [
        "build/*",
        "setup.py",
        "test*",
        "example*",
        "sample*",
        "doc*",
        "azure/__init__.py",
        "azure/mltable/__init__.py"
    ]
    def form_exclude_path(raletive_path):
        return os.path.join(source_folder, raletive_path)
    assert exclude_path == [form_exclude_path(path) for path in expected_exclude_path]

def test_get_exclude_command_check_extra_exclude(tmp_path):
    source_folder = os.path.join(tmp_path,"source_folder")
    yaml_output_folder = os.path.join(tmp_path,"yaml_output_folder")
    package_info_2.path = Source(
        source_folder = source_folder, yaml_output_folder = yaml_output_folder, package_name = 'azure-core-tracing-opencensus'
    )
    exclude_path = package_info_2.get_exluded_command()
    expected_exclude_path = [
        "build/*",
        "setup.py",
        "azure/__init__.py",
        "azure/core/__init__.py",
        "azure/core/tracing/__init__.py",
        'azure/core/tracing/ext/__init__.py'
    ]
    def form_exclude_path(raletive_path):
        return os.path.join(source_folder, raletive_path)
    assert exclude_path == [form_exclude_path(path) for path in expected_exclude_path]