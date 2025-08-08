import os.path as path
import os
import subprocess
import sys

import py2docfx.convert_prepare.git as git
import py2docfx.convert_prepare.pip_utils as pip_utils
import py2docfx.convert_prepare.pack as pack
from py2docfx.docfx_yaml.logger import get_logger
from py2docfx.convert_prepare.constants import TARGET_REPO, SOURCE_REPO, DIST_TEMP
from py2docfx.convert_prepare.install_package import install_package
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.source import Source

YAML_OUTPUT_ROOT =  path.join(TARGET_REPO, "docs-ref-autogen")

def update_package_info(executable: str, pkg: PackageInfo, source_folder: str):
    cur_path = os.getcwd()
    os.chdir(source_folder) # TODO: replace it

    all_files = os.listdir()
    files = [f for f in all_files if path.isfile(f)]

    # update package attributes
    attrs = ["name", "version", "author"]
    if "setup.py" in files:
        for attr in attrs:
            proc_ret = subprocess.run(
                [executable, "setup.py", "--quiet", "--dry-run", f"--{attr}"],
                capture_output=True,
                text=True,
                check=True
            )

            if isinstance(proc_ret.stdout, list):
                attr_val = (proc_ret.stdout[-1]).strip()
            elif '\n' in proc_ret.stdout:
                attr_val = proc_ret.stdout.strip().split('\n')[-1]
            else:
                attr_val = proc_ret.stdout.strip()

            setattr(pkg, attr, attr_val)
    else:
        # Find .dist-info folders
        dist_info_folders = [f for f in all_files if path.isdir(f) and f.endswith(".dist-info")]
        
        if dist_info_folders:
            folder = dist_info_folders[0]  # Take the first one if multiple exist
            if path.exists(path.join(folder, "METADATA")):
                with open(
                    path.join(folder, "METADATA"), "r", encoding="utf-8"
                ) as file_handle:
                    metadata = file_handle.readlines()
                for meta_info in metadata:
                    meta_info_array = meta_info.split(":")
                    meta_field = meta_info_array[0].strip().lower()
                    if meta_field in attrs:
                        setattr(
                            pkg,
                            meta_field,
                            ":".join(meta_info_array[1:]).strip(),
                        )
            else:
                package_full_name = path.basename(folder)
                package_info = package_full_name.replace(
                    ".dist-info", "").split("-")
                pkg.name = "-".join(package_info[0:-1]).strip()
                pkg.version = package_info[-1].strip()

    # update package path
    os.chdir(cur_path) # TODO: replace it
    yaml_output_folder = path.join(YAML_OUTPUT_ROOT, pkg.name)
    pkg.path = Source(
        source_folder=source_folder, yaml_output_folder=yaml_output_folder, package_name=pkg.name
    )

async def get_source(executable: str, pkg: PackageInfo, cnt: int, vststoken=None, githubtoken=None, is_required_pkg=False):
    py2docfx_logger = get_logger(__name__)
    path_cnt = str(cnt)
    if is_required_pkg:
        path_cnt = "required_" + path_cnt
    dist_dir = path.join(DIST_TEMP, path_cnt)

    if pkg.install_type == PackageInfo.InstallType.SOURCE_CODE:
        if pkg.url:
            repo_folder = path.join(SOURCE_REPO, path_cnt)
            token = githubtoken if "github.com" in pkg.url else vststoken
            source_folder = await git.clone(
                repo_location=pkg.url,
                branch=pkg.branch,
                folder=repo_folder,
                extra_token=token,
            )
            if pkg.folder:
                source_folder = path.join(source_folder, pkg.folder)
        else:
            source_folder = pkg.folder
            sys.path.insert(0, source_folder)
    elif pkg.install_type == PackageInfo.InstallType.PYPI:
        full_name = pkg.get_combined_name_version()
        # Ensure the dist directory exists
        os.makedirs(dist_dir, exist_ok=True)
        
        await pip_utils.download(
            full_name,
            dist_dir,
            extra_index_url=pkg.extra_index_url,
            prefer_source_distribution=pkg.prefer_source_distribution,
        )
        # unpack the downloaded wheel file.
        dist_files = os.listdir(dist_dir)
        if not dist_files:
            msg = f"No files downloaded to {dist_dir} for package {pkg.name}"
            py2docfx_logger.error(msg)
            raise FileNotFoundError(f"No files found in {dist_dir}")
            
        downloaded_dist_file = path.join(dist_dir, dist_files[0])
        await pack.unpack_dist(pkg.name, downloaded_dist_file)
        os.remove(downloaded_dist_file)
        dist_files = os.listdir(dist_dir)
        if not dist_files:
            msg = f"No files found in {dist_dir} after unpacking for package {pkg.name}"
            py2docfx_logger.error(msg)
            raise FileNotFoundError(f"No files found in {dist_dir} after unpacking")
            
        source_folder = path.join(
            path.dirname(downloaded_dist_file),
            dist_files[0]
        )
    elif pkg.install_type == PackageInfo.InstallType.DIST_FILE:
        # Ensure the dist directory exists
        os.makedirs(dist_dir, exist_ok=True)
        
        await pip_utils.download(pkg.location, dist_dir, prefer_source_distribution=False)
        # unpack the downloaded dist file.
        dist_files = os.listdir(dist_dir)
        if not dist_files:
            msg = f"No files downloaded to {dist_dir} for package {pkg.name}"
            py2docfx_logger.error(msg)
            raise FileNotFoundError(f"No files found in {dist_dir}")
            
        downloaded_dist_file = path.join(dist_dir, dist_files[0])
        await pack.unpack_dist(pkg.name, downloaded_dist_file)
        os.remove(downloaded_dist_file)
        
        # Check again after unpacking
        dist_files = os.listdir(dist_dir)
        if not dist_files:
            msg = f"No files found in {dist_dir} after unpacking for package {pkg.name}"
            py2docfx_logger.error(msg)
            raise FileNotFoundError(f"No files found in {dist_dir} after unpacking")
        if downloaded_dist_file.endswith(".tar.gz"):
            downloaded_dist_file = downloaded_dist_file.rsplit(".", maxsplit=1)[
                0]
        source_folder = path.join(
            path.dirname(downloaded_dist_file),
            dist_files[0] if dist_files else ""
        )
    else:
        msg = f"Unknown install type: {pkg.install_type}"
        py2docfx_logger.error(msg)
        raise ValueError(msg)

    update_package_info(executable, pkg, source_folder)
