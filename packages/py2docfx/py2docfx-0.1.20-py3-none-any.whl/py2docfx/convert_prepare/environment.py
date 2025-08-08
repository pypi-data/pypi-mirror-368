import subprocess
import asyncio
import os
import sys

from py2docfx import PACKAGE_ROOT
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.get_source import get_source
from py2docfx.convert_prepare import pip_utils
from py2docfx.docfx_yaml.logger import get_logger, run_async_subprocess

REQUIREMENT_MODULES = ["setuptools", "sphinx==6.1.3", "pyyaml", "jinja2==3.0.3", "wheel"]
VENV_REQUIREMENT_MODULES = ["setuptools", "wheel"] # to support running setup.py in venv
VENV_DIR = "venv"
VENV_BUFFER = 10
VENV_DELETE_BUFFER = 10
PIP_INSTALL_COMMAND = ["-m", "pip", "install", "--upgrade"] 

PIP_INSTALL_VENV_COMMON_OPTIONS = [
    "--quiet",
    "--no-warn-conflicts",
    "--disable-pip-version-check",
]

async def install_converter_requirements(executable: str):
    """
    Install setuptools/sphinx/pyyaml/jinja2
    Replacing logic of
    https://apidrop.visualstudio.com/Content%20CI/_git/ReferenceAutomation?path=/Python/InstallPackage.ps1&line=15&lineEnd=35&lineStartColumn=1&lineEndColumn=87&lineStyle=plain&_a=contents
    """
    pip_install_cmd = [executable, "-m", "pip", "install", "--upgrade"]
    py2docfx_logger = get_logger(__name__)
    pip_install_common_options = [
        "--no-cache-dir",
        "--quiet",
        "--no-compile",
        "--no-warn-conflicts",
        "--disable-pip-version-check",
    ]

    for module in REQUIREMENT_MODULES:
        msg = f"<CI INFO>: Upgrading {module}..."
        py2docfx_logger.info(msg)
        full_cmd = pip_install_cmd + [module] + pip_install_common_options
        await run_async_subprocess(executable, full_cmd, py2docfx_logger)

async def install_venv_requirements(venv_num: int):
    venv_exe = get_venv_exe(venv_num)
    pip_cmd = ["-m", "pip", "install", "--upgrade"]+ VENV_REQUIREMENT_MODULES
    py2docfx_logger = get_logger(__name__)
    await run_async_subprocess(venv_exe, pip_cmd, py2docfx_logger)

def get_venv_path(venv_num: int) -> str:
    return os.path.join(PACKAGE_ROOT, VENV_DIR, "venv"+str(venv_num))

def get_base_venv_path() -> str:
    return os.path.join(PACKAGE_ROOT, VENV_DIR, "basevenv")

def get_venv_exe(venv_num: int) -> str:
    if os.name == 'nt':
        return os.path.join(get_venv_path(venv_num), "Scripts", "python.exe")
    else:
        return os.path.join(get_venv_path(venv_num), "bin", "python3")

def get_base_venv_exe() -> str:
    if os.name == 'nt':
        return os.path.join(get_base_venv_path(), "Scripts", "python.exe")
    else:
        return os.path.join(get_base_venv_path(), "bin", "python3")

def get_venv_package_path(venv_num: int) -> str:
    if os.name == 'nt':  # Windows
        return os.path.join(get_venv_path(venv_num), "Lib", "site-packages")
    else:  # Linux and other Unix-like systems
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}" # venv version should be same as native
        return os.path.join(get_venv_path(venv_num), "lib", python_version, "site-packages")

def get_base_venv_sphinx_build_path() -> str:
    if os.name == 'nt':  # Windows
        return os.path.join(get_base_venv_path(), "Lib", "site-packages", "sphinx", "cmd", "build.py")
    else: # Linux and other Unix-like systems
        python_version = f"python{sys.version_info.major}.{sys.version_info.minor}" # venv version should be same as native
        return os.path.join(get_base_venv_path(), "lib", python_version, "site-packages", "sphinx", "cmd", "build.py")
        

async def install_converter_requirement_async(executable: str):
    pip_cmd = PIP_INSTALL_COMMAND + PIP_INSTALL_VENV_COMMON_OPTIONS + REQUIREMENT_MODULES
    py2docfx_logger = get_logger(__name__)
    await run_async_subprocess(executable, pip_cmd, py2docfx_logger)

async def install_required_packages(
        executable: str, required_package_list: list[PackageInfo], github_token: str, ado_token: str):
    for package in required_package_list:
        idx = required_package_list.index(package)
        if package.install_type == package.InstallType.SOURCE_CODE:
            await get_source(executable, package, idx, vststoken=ado_token, githubtoken=github_token, is_required_pkg=True)
        package_name, options = package.get_install_command()
        pip_cmd = PIP_INSTALL_COMMAND + PIP_INSTALL_VENV_COMMON_OPTIONS + options + [package_name]
        py2docfx_logger = get_logger(__name__)
        await run_async_subprocess(executable, pip_cmd, py2docfx_logger)

async def create_environment(venv_path: int):
    if os.name == 'nt':
        await (await asyncio.create_subprocess_exec("python", "-m", "venv", venv_path)).wait()
    else: # On linux the default command name is
        await (await asyncio.create_subprocess_exec("python3", "-m", "venv", venv_path)).wait()

async def prepare_base_venv(required_package_list: list[PackageInfo], github_token: str, ado_token: str):
    py2docfx_logger = get_logger(__name__)
    
    msg = f"<CI INFO>: Creating basevenv..."
    py2docfx_logger.info(msg)
    await create_environment(get_base_venv_path())
    
    msg = f"<CI INFO>: Installing converter requirements in ..."
    py2docfx_logger.info(msg)
    await install_converter_requirement_async(get_base_venv_exe())
    
    msg = f"<CI INFO>: Installing required packages in basevenv..."
    py2docfx_logger.info(msg)
    await install_required_packages(get_base_venv_exe(), required_package_list, github_token, ado_token)
    
    msg = f"<CI INFO>: basevenv setup complete."
    py2docfx_logger.info(msg)

async def prepare_venv(venv_num: int, package_info: PackageInfo, package_number: int, github_token: str, ado_token: str):
    py2docfx_logger = get_logger(__name__)
    await create_environment(get_venv_path(venv_num))
    await install_venv_requirements(venv_num)
    await get_source(get_venv_exe(venv_num), package_info, package_number, vststoken=ado_token, githubtoken=github_token)
    package_name, options = package_info.get_install_command()
    await pip_utils.install_in_exe_async(get_venv_exe(venv_num), package_name, options)
    msg = f"<CI INFO>: venv{venv_num} setup complete."
    py2docfx_logger.info(msg)

async def remove_environment(venv_num: int):
    py2docfx_logger = get_logger(__name__)
    venv_path = get_venv_path(venv_num)
    if os.path.exists(venv_path):
        msg = f"<CI INFO>: Removing venv{venv_num}..."
        py2docfx_logger.info(msg)
        # Create a subprocess to run the shell command for removing the directory
        cmd = f'rm -rf {venv_path}' if os.name != 'nt' else f'rmdir /S /Q {venv_path}'
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            msg = f"<CI INFO>: venv{venv_num} removed."
            py2docfx_logger.info(msg)
        else:
            msg = f"<CI ERROR>: Failed to remove venv{venv_num}. Error: {stderr.decode()}"
            py2docfx_logger.error(msg)
            raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
