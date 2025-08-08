import tarfile
import zipfile
import os
import subprocess
import shutil
import glob
from os import path
import pytest

from py2docfx.convert_prepare.pack import unpack_compressed, unpack_wheel

SRC_DIR = path.abspath("convert_prepare/tests/data/pack/")


def _assert_file_list_same(
    src, target, source_exclude_patterns=[], target_exclude_patterns=[]
):
    src_files = set(
        [
            path.relpath(path.join(dn, file_name), src)
            for dn, _, f in os.walk(src)
            for file_name in f
        ]
    )
    unpacked_files = set(
        [
            path.relpath(path.join(dn, file_name), target)
            for dn, _, f in os.walk(target)
            for file_name in f
        ]
    )

    for pattern in source_exclude_patterns:
        src_files = src_files - set([path.relpath(f, src) for f in glob.glob(pattern)])
    for pattern in target_exclude_patterns:
        unpacked_files = unpacked_files - set(
            [path.relpath(f, target) for f in glob.glob(pattern)]
        )

    assert src_files == unpacked_files


def test_pack_unpack_compressed(tmp_path):
    def _prepare_compressed_gz(target_path):
        archive_file_path = target_path / "test_pack_unpack_compressed.tar.gz"
        with tarfile.open(archive_file_path, "w:gz") as tar:
            for dirname, _, files in os.walk(SRC_DIR):
                for filename in files:
                    absname = path.abspath(path.join(dirname, filename))
                    arcname = absname[len(SRC_DIR) + 1 :]
                    tar.add(absname, arcname)
        return archive_file_path

    def _prepare_compressed_zip(target_path):
        archive_file_path = target_path / "test_pack_unpack_compressed.zip"
        with zipfile.ZipFile(archive_file_path, "w") as zip:
            for dirname, _, files in os.walk(SRC_DIR):
                for filename in files:
                    absname = path.abspath(path.join(dirname, filename))
                    arcname = absname[len(SRC_DIR) + 1 :]
                    zip.write(absname, arcname)
        return archive_file_path

    # prepare the compressed file in target test folder
    zip_path = tmp_path / "zip"
    os.makedirs(zip_path)
    zip_file_path = _prepare_compressed_zip(zip_path)

    # unpack and assert the file list
    unpack_compressed(zip_file_path)
    _assert_file_list_same(
        path.abspath("convert_prepare/tests/data/pack"), tmp_path / "zip", [], [str(zip_file_path)]
    )

    # prepare the compressed file in target test folder
    gz_path = tmp_path / "gz"
    os.makedirs(gz_path)
    gz_file_path = _prepare_compressed_gz(gz_path)

    # unpack and assert the file list
    unpack_compressed(gz_file_path)
    _assert_file_list_same(
        path.abspath("convert_prepare/tests/data/pack"), tmp_path / "gz", [], [str(gz_file_path)]
    )

@pytest.mark.asyncio
async def test_pack_unpack_wheel(tmp_path):
    def _prepare_wheel(target_path):
        subprocess.run(
            ["pip", "wheel", ".", "--wheel-dir", str(target_path / "wheel")],
            cwd=SRC_DIR,
        )

        # remove the build folder and egg-info folder generated when build wheels which we don't care
        if path.exists(path.join(SRC_DIR, "build")):
            shutil.rmtree(path.join(SRC_DIR, "build"))
        if path.exists(path.join(SRC_DIR, "foo.egg-info")):
            shutil.rmtree(path.join(SRC_DIR, "foo.egg-info"))

    os.makedirs(tmp_path / "wheel")
    _prepare_wheel(tmp_path)

    # find the wheel file
    wheel_name = [
        f
        for f in os.listdir(tmp_path / "wheel")
        if f.endswith(".whl") and path.isfile(path.join(tmp_path / "wheel", f))
    ][0]
    wheel_path = path.join(tmp_path / "wheel", wheel_name)

    # unpack and assert the file list
    package_name = wheel_name.split("-")[0]
    await unpack_wheel(package_name, wheel_path)
    _assert_file_list_same(
        path.abspath("convert_prepare/tests/data/pack"),
        tmp_path / "wheel" / "foo-0.1",
        [str(path.join(SRC_DIR, "pyproject.toml"))],
        [str(wheel_path), str(tmp_path / "wheel" / "foo-0.1") + "/*.dist-info/**"],
    )
