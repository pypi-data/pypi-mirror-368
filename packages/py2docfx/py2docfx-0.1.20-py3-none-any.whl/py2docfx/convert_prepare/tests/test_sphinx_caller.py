import os
import pytest
import shutil
import sphinx
import sphinx.cmd.build

from py2docfx.convert_prepare.sphinx_caller import run_apidoc, run_converter
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.source import Source

package_info = PackageInfo()

def init_paths(tmp_path):
    rst_path = os.path.join(tmp_path, "test_rst")

    source_code_path = os.path.abspath("convert_prepare/tests/data/sphinx_caller/test_source_code")
    destination = os.path.join(tmp_path, "test_source_code")
    shutil.copytree(source_code_path, destination)

    package_info.code_location = destination
    package_info.exclude_path = ["testcode/exclude/*"]
    package_info.path = Source(source_folder=destination, yaml_output_folder=rst_path, package_name="testcode")
    package_info.build_in_subpackage = False
    package_info.name = 'testcode'
    return rst_path, destination

@pytest.mark.asyncio
async def test_run_apidoc(tmp_path):
    rst_path, source_code_path = init_paths(tmp_path)
    package_name = "testcode"
    await run_apidoc(package_name, rst_path, source_code_path, package_info.get_exluded_command(), package_info)

    # List all files under rst_path
    rst_list = os.listdir(rst_path)
    assert "testcode.fakemodule.rst" in rst_list
    assert "testcode.exclude.rst" not in rst_list

@pytest.mark.asyncio
async def test_run_converter(tmp_path):
    rst_path, source_code_path = init_paths(tmp_path)
    package_name = "testcode"
    await run_apidoc(package_name, rst_path, source_code_path, package_info.get_exluded_command(), package_info)

    # prepare conf.py, index.rst and docfx_yaml
    conf_path = os.path.abspath("convert_prepare/tests/data/sphinx_caller/conf.py")
    destination = os.path.join(rst_path)
    shutil.copy(conf_path, destination)
    docfx_yaml_path = os.path.abspath("docfx_yaml")
    shutil.copytree(docfx_yaml_path, os.path.join(tmp_path, "docfx_yaml"))
    with open(os.path.join(rst_path, "index.rst"), "w", encoding="utf-8") as index_rst:
        index_rst.write("")

    out_path = os.path.join(tmp_path, "out")
    out_path = await run_converter(package_name, rst_path, out_path, sphinx_build_path = sphinx.cmd.build.__file__, extra_package_path = source_code_path, conf_path=rst_path)

    if os.path.exists(out_path):
        yaml_list = os.listdir(os.path.join(out_path, "docfx_yaml"))
        assert "testcode.fakemodule.test_code.yml" in yaml_list
        assert "testcode.fakemodule.test_code.testClass.yml" in yaml_list
        assert "toc.yml" in yaml_list
        assert "testcode.exclude.exclude.yml" not in yaml_list
        assert "testcode.exclude.exclude.exclude.yml" not in yaml_list
    else:
        assert False
