import shutil
from os import path
import os
import sys

from py2docfx.docfx_yaml.logger import get_package_logger, run_async_subprocess

async def unpack_dist(package_name, dist_file):
    if dist_file.endswith(".whl"):
        await unpack_wheel(package_name, dist_file)
    else:
        unpack_compressed(dist_file)

def unpack_compressed(file_path):
    """
    Transform a tar.gz/zip file to a folder containing source code
    """

    shutil.unpack_archive(file_path, path.dirname(file_path))


async def unpack_wheel(package_name, file_path):
    """
    Transform a wheel file to a folder containing source code
    """
    py2docfx_logger = get_package_logger(__name__, package_name)
    command = ['-m',
               'wheel',
               'unpack',
               file_path,
               '-d',
               os.path.dirname(file_path)]
    await run_async_subprocess(sys.executable, command, py2docfx_logger)
    extract_folder = [file for file in os.listdir(path.dirname(file_path)) if path.isdir(path.join(path.dirname(file_path), file))][0]
    data_folder = path.join(path.dirname(file_path), extract_folder, extract_folder + ".data")
    if path.exists(data_folder):
        for subfolder in ["purelib", "platlib"]:
            if path.exists(path.join(data_folder, subfolder)):
                for file in os.listdir(path.join(data_folder, subfolder)):
                    shutil.move(path.join(data_folder, subfolder, file), path.join(path.dirname(file_path), extract_folder))
        shutil.rmtree(data_folder)
