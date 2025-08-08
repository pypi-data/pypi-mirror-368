"""
Test the generate_document function.
"""
import os
import sys
import shutil
import pytest
import sphinx
import sphinx.cmd.build

from py2docfx.convert_prepare.generate_document import generate_document
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.source import Source

@pytest.mark.asyncio
async def test_generate_document(tmp_path):
    """
    Test the generate_document function.
    """
    # init test case
    source_code_path = os.path.join("convert_prepare", "tests", "data", "generate_document")
    output_root = os.path.join(tmp_path, "output")
    shutil.copytree(source_code_path, os.path.join(tmp_path, "source", "0"))
    package = PackageInfo()
    package.name = "azure-dummy-sourcecode"
    package.exclude_path = ["test*", "example*", "sample*", "doc*"]
    package.install_type = PackageInfo.InstallType.PYPI
    package.version = None
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = False
    source_folder = os.path.join(tmp_path, "source", "0", "azure-dummy-sourcecode")
    yaml_output_folder = os.path.join(tmp_path, "yaml_output")
    package.path = Source(
        source_folder=source_folder, yaml_output_folder=yaml_output_folder, package_name=package.name
    )

    # add dummy code to python sys path to simulate installation
    os.environ["PYTHONPATH"] = os.path.abspath(source_folder)
    sys.path.insert(0, os.path.abspath(source_folder))

    # add docfx_yaml to python sys path for sphinx build to import
    sys.path.insert(1, os.path.abspath("docfx_yaml"))

    # call the function
    
    await generate_document(package, output_root, sphinx_build_path = sphinx.cmd.build.__file__, extra_package_path = source_folder)

    #assert the result
    yaml_path = os.path.join(yaml_output_folder, "_build", "docfx_yaml")
    assert os.path.exists(yaml_path)
    assert os.path.exists(os.path.join(yaml_path, "azure.dummy.sourcecode.foo.foo.yml"))
    assert os.path.exists(os.path.join(yaml_path, "azure.dummy.sourcecode.boo.boo.yml"))
    assert os.path.exists(os.path.join(yaml_path, "azure.dummy.sourcecode.foo.foo.Foo.yml"))
    assert os.path.exists(os.path.join(yaml_path, "azure.dummy.sourcecode.boo.boo.Boo.yml"))
    assert os.path.exists(os.path.join(yaml_path, "azure.dummy.sourcecode.yml"))
    assert not os.path.exists(os.path.join(yaml_path, "azure.dummy.yml"))
    assert not os.path.exists(os.path.join(yaml_path, "azure.yml"))
    assert os.path.exists(os.path.join(yaml_path, "toc.yml"))
