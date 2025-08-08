import os
import shutil
import pytest

from py2docfx.convert_prepare.constants import SOURCE_REPO, TARGET_REPO, DIST_TEMP
from py2docfx.convert_prepare.environment import (
    get_venv_path,
    create_environment,
    get_venv_exe,
    install_venv_requirements,
    remove_environment,
    prepare_base_venv,
    get_base_venv_exe,
    get_base_venv_path,
    install_required_packages,
    VENV_REQUIREMENT_MODULES
)
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.utils import temp_folder_clean_up

@pytest.mark.asyncio
async def test_venv_creation_package_install_remove():
    # Test creating a venv
    venv_path = get_venv_path(0)
    await create_environment(venv_path)
    interpreter = get_venv_exe(0)
    assert os.path.exists(interpreter)

    # Test installing requirements
    await install_venv_requirements(0)
    # check if the requirements are installed in the venv
    for module in VENV_REQUIREMENT_MODULES:
        assert os.system(f"{interpreter} -m pip show {module}") == 0

    # Test removing the venv
    await remove_environment(0)
    assert not os.path.exists(interpreter)

@pytest.mark.asyncio
async def test_prepare_base_venv():
    await prepare_base_venv([], "", "")
    interpreter = get_base_venv_exe()
    assert os.path.exists(interpreter)
    # check if the requirements are installed in the venv
    requrirements = ["setuptools", "sphinx", "pyyaml", "jinja2", "wheel"]
    for module in requrirements:
        assert os.system(f"{interpreter} -m pip show {module}") == 0

    # remove base venv
    base_venv_path = get_base_venv_path()
    shutil.rmtree(base_venv_path)

@pytest.mark.asyncio
async def test_install_required_packages_pypi():
    required_package_info = PackageInfo()
    required_package_info.install_type = PackageInfo.InstallType.PYPI
    required_package_info.name = "azure-core"

    await prepare_base_venv([], "", "")
    interpreter = get_base_venv_exe()
    await install_required_packages(interpreter, [required_package_info], None, None)
    
    assert os.system(f"{interpreter} -m pip show {required_package_info.name}") == 0

@pytest.mark.asyncio
async def test_install_required_packages_source_code():
    temp_folder_clean_up([SOURCE_REPO, TARGET_REPO, DIST_TEMP])
    required_package_info = PackageInfo()
    required_package_info.install_type = PackageInfo.InstallType.SOURCE_CODE
    required_package_info.name = "sklearn-pandas"
    required_package_info.url = "https://github.com/scikit-learn-contrib/sklearn-pandas"
    required_package_info.branch = "master"
    required_package_info.folder = "."

    await prepare_base_venv([], "", "")
    interpreter = get_base_venv_exe()
    await install_required_packages(interpreter, [required_package_info], None, None)
    
    assert os.system(f"{interpreter} -m pip show {required_package_info.name}") == 0

@pytest.mark.asyncio
async def test_install_required_packages_dist_file():
    temp_folder_clean_up([SOURCE_REPO, TARGET_REPO, DIST_TEMP])
    required_package_info = PackageInfo()
    required_package_info.install_type = PackageInfo.InstallType.DIST_FILE
    required_package_info.name = "azure-core"
    required_package_info.location = "https://files.pythonhosted.org/packages/39/83/325bf5e02504dbd8b4faa98197a44cdf8a325ef259b48326a2b6f17f8383/azure_core-1.32.0-py3-none-any.whl"

    await prepare_base_venv([], "", "")
    interpreter = get_base_venv_exe()
    await install_required_packages(interpreter, [required_package_info], None, None)
    
    assert os.system(f"{interpreter} -m pip show {required_package_info.name}") == 0