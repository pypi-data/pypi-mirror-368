"""
This is a unit test module for the functions in get_source.py
"""
import os
import shutil
import stat
import pytest
import sys

from py2docfx.convert_prepare import git
from py2docfx.convert_prepare import get_source
from py2docfx.convert_prepare.package_info import PackageInfo

@pytest.fixture(scope='module', name="init_package_info")
def fixture_init_package_info() -> PackageInfo:
    """
    Initialize a new PackageInfo object to reduce redundant code
    """
    package = PackageInfo()
    package.name = "inital_name"
    package.exclude_path = ["test*", "example*", "sample*", "doc*"]
    return package

def init_clean_up():
    """
    Initialize the clean up process
    """
    if os.path.exists("source_repo"):
        
        def remove_readonly(func, path, excinfo):
        # There are some read-only files in a git repo
        # Change them into writable so that they coule be removed
        # Reference link https://stackoverflow.com/a/58878271
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)

        shutil.rmtree("source_repo", onerror = remove_readonly)
    if os.path.exists("dist_temp"):
        shutil.rmtree("dist_temp")

def test_update_package_info(init_package_info):
    """
    Test the function update_package_info
    """
    package = init_package_info
    base_path = "convert_prepare/tests/data/get_source/"

    # case of setup.py
    get_source.update_package_info(sys.executable, package, os.path.join(base_path, "mock-1"))
    assert package.name == "dummy_package"
    assert package.version == "3.1.0"

    # case of metadata
    package = init_package_info
    get_source.update_package_info(sys.executable, package, os.path.join(base_path, "mock-2"))
    assert package.name == "mock_package"
    assert package.version == "2.2.0"

    # case of dist-info folder
    package = init_package_info
    get_source.update_package_info(sys.executable, package, os.path.join(base_path, "mock-3"))
    assert package.name == "mock_package"
    assert package.version == "1.2.0"

@pytest.mark.asyncio
async def test_get_source_git_clone(init_package_info):
    """
    Test the git clone of get_source
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-iot-hub-python"
    package.install_type = PackageInfo.InstallType.SOURCE_CODE
    package.version = None
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    package.branch = "main"
    package.folder = None
    package.url = "https://github.com/Azure/azure-iot-hub-python"
    await get_source.get_source(sys.executable, package, 0)
    assert git.status("source_repo/0") is True

@pytest.mark.asyncio
async def test_get_source_dist_file_zip(init_package_info):
    """
    Test the zip dist file download of get_source
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-common"
    package.install_type = PackageInfo.InstallType.DIST_FILE
    package.version = None
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    package.location = "https://files.pythonhosted.org/packages/3e/71/f6f71a276e2e69264a97ad39ef850dca0a04fce67b12570730cb38d0ccac/azure-common-1.1.28.zip"
    await get_source.get_source(sys.executable, package, 1)
    assert os.path.exists("dist_temp/1/azure-common-1.1.28")
    assert package.path.source_folder == os.path.join("dist_temp", "1", "azure-common-1.1.28")
    assert os.path.exists("dist_temp/1/azure-common-1.1.28.zip") is False

@pytest.mark.asyncio
async def test_get_source_dist_file_whl(init_package_info):
    """
    Test the whl dist file download of get_source
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-common"
    package.install_type = PackageInfo.InstallType.DIST_FILE
    package.version = None
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    package.location = "https://files.pythonhosted.org/packages/62/55/7f118b9c1b23ec15ca05d15a578d8207aa1706bc6f7c87218efffbbf875d/azure_common-1.1.28-py2.py3-none-any.whl"
    await get_source.get_source(sys.executable, package, 2)
    assert os.path.exists("dist_temp/2/azure_common-1.1.28")
    assert package.path.source_folder == os.path.join("dist_temp", "2", "azure_common-1.1.28")
    assert os.path.exists("dist_temp/2/azure_common-1.1.28-py2.py3-none-any.whl") is False

@pytest.mark.asyncio
async def test_get_source_dist_file_tar(init_package_info):
    """
    Test the tar dist file download of get_source
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-core"
    package.install_type = PackageInfo.InstallType.DIST_FILE
    package.version = None
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    package.location = "https://files.pythonhosted.org/packages/fa/19/43a9eb812b4d6071fdc2c55640318f7eb5a1be8dbd3b6f9d96a1996e1bb6/azure-core-1.29.4.tar.gz"
    await get_source.get_source(sys.executable, package, 3)
    assert os.path.exists("dist_temp/3/azure-core-1.29.4")
    assert package.path.source_folder == os.path.join("dist_temp", "3", "azure-core-1.29.4")
    assert os.path.exists("dist_temp/3/azure-core-1.29.4.tar.gz") is False

@pytest.mark.asyncio
async def test_get_source_pip_whl(init_package_info):
    """
    Test the pip install of get_source with prefer_source_distribution = False
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-common"
    package.install_type = PackageInfo.InstallType.PYPI
    package.version = "1.1.28"
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = False
    await get_source.get_source(sys.executable, package, 4)
    assert os.path.exists("dist_temp/4/azure_common-1.1.28")
    assert package.path.source_folder == os.path.join("dist_temp", "4", "azure_common-1.1.28")
    assert os.path.exists("dist_temp/4/azure_common-1.1.28-py2.py3-none-any.whl") is False

@pytest.mark.asyncio
async def test_get_source_pip_zip(init_package_info):
    """
    Test the pip install of get_source with prefer_source_distribution = True
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-common"
    package.install_type = PackageInfo.InstallType.PYPI
    package.version = "1.1.28"
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    await get_source.get_source(sys.executable, package, 5)
    assert os.path.exists("dist_temp/5/azure-common-1.1.28")
    assert package.path.source_folder == os.path.join("dist_temp", "5", "azure-common-1.1.28")
    assert os.path.exists("dist_temp/5/azure-common-1.1.28.zip") is False

@pytest.mark.asyncio
async def test_get_source_zip_file_at_position_0(init_package_info):
    """
    Test the pip install of packages with zip or tar file at position 0 in the dirctory list
    """
    init_clean_up()
    package = init_package_info
    package.name = "azure-template"
    package.install_type = PackageInfo.InstallType.PYPI
    package.version = "0.1.0b3942895"
    package.build_in_subpackage = False
    package.extra_index_url = None
    package.prefer_source_distribution = True
    await get_source.get_source(sys.executable, package, 6)
    assert os.path.exists("dist_temp/6/azure_template-0.1.0b3942895")
    assert package.path.source_folder == os.path.join("dist_temp", "6", "azure_template-0.1.0b3942895")
    assert os.path.exists("dist_temp/6/azure_template-0.1.0b3942895.tar.gz") is False
