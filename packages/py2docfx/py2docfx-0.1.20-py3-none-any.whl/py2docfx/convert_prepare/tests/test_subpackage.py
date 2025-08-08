import shutil, os, yaml
from os import path

from py2docfx.convert_prepare.subpackage import (
    get_subpackages,
    move_rst_files_to_subfolder,
    merge_subpackage_files,
)

SRC_DIR = path.abspath("convert_prepare/tests/data/subpackage/azure-mgmt-containerservice")
RST_DIR = path.abspath("convert_prepare/tests/data/subpackage/azure-mgmt-containerservice-RST")
MERGE_DIR = path.abspath("convert_prepare/tests/data/subpackage/azure-mgmt-containerservice-merge")


def test_get_subpackages():
    expected = ["aio", "v2017_07_01", "v2018_03_31"]
    actual = get_subpackages(SRC_DIR, "azure-mgmt-containerservice")
    assert set(expected) == set(actual)


def test_move_rst_files_to_subfolder(tmp_path):
    # prepare
    tmp_RST_path = path.join(tmp_path, "rst")
    shutil.copytree(RST_DIR, tmp_RST_path)

    subpackages_path_record = move_rst_files_to_subfolder(
        tmp_RST_path,
        "azure-mgmt-containerservice",
        get_subpackages(SRC_DIR, "azure-mgmt-containerservice"),
    )

    expected_folder_structure = set(
        [
            path.relpath(path.join(tmp_RST_path, rst_path), tmp_RST_path)
            for rst_path in [
                "azure.mgmt.containerservice.rst",
                "subpackages/aio/index.rst",
                "subpackages/aio/azure.mgmt.containerservice.aio.rst",
                "subpackages/v2017_07_01/index.rst",
                "subpackages/v2017_07_01/azure.mgmt.containerservice.v2017_07_01.rst",
                "subpackages/v2018_03_31/index.rst",
                "subpackages/v2018_03_31/azure.mgmt.containerservice.v2018_03_31.rst",
                "subpackages/v2018_03_31/azure.mgmt.containerservice.v2018_03_31.models.rst",
            ]
        ]
    )

    # assert
    actual_folder_structure = set()
    for dirname, _, files in os.walk(tmp_RST_path):
        for file in files:
            actual_folder_structure.add(
                path.relpath(path.join(dirname, file), tmp_RST_path)
            )

    assert expected_folder_structure == actual_folder_structure

    expected_return = {
        "aio": path.abspath(path.join(tmp_RST_path, "subpackages/aio")),
        "v2017_07_01": path.abspath(path.join(tmp_RST_path, "subpackages/v2017_07_01")),
        "v2018_03_31": path.abspath(path.join(tmp_RST_path, "subpackages/v2018_03_31")),
    }
    assert expected_return == subpackages_path_record


def test_merge_subpackage_files(tmp_path):
    # prepare
    tmp_RST_path = path.join(tmp_path, "rst")
    shutil.copytree(RST_DIR, tmp_RST_path)
    subpackages_path_record = move_rst_files_to_subfolder(
        tmp_RST_path,
        "azure-mgmt-containerservice",
        get_subpackages(SRC_DIR, "azure-mgmt-containerservice"),
    )
    tmp_doc_path = path.join(tmp_path, "merge")
    shutil.copytree(MERGE_DIR, tmp_doc_path)

    merge_subpackage_files(
        dict(
            [
                (name, path.join(subpackage_path.replace("rst", "merge"), "_build"))
                for (name, subpackage_path) in subpackages_path_record.items()
            ]
        ),
        path.abspath(path.join(tmp_doc_path, "doc/_build")),
        "azure-mgmt-containerservice",
    )

    # assert
    expected_folder_structure = [
        "azure.mgmt.containerservice.aio.ContainerServiceClient.yml",
        "azure.mgmt.containerservice.aio.yml",
        "azure.mgmt.containerservice.ContainerServiceClient.yml",
        "azure.mgmt.containerservice.models.yml",
        "azure.mgmt.containerservice.v2017_07_01.ContainerServiceClient.yml",
        "azure.mgmt.containerservice.v2017_07_01.yml",
        "azure.mgmt.containerservice.v2018_03_31.models.yml",
        "azure.mgmt.containerservice.v2018_03_31.yml",
        "azure.mgmt.containerservice.yml",
        "index.yml",
        "toc.yml",
    ]
    assert set(expected_folder_structure) == set(
        [f.name for f in os.scandir(path.join(tmp_doc_path, "doc/_build/docfx_yaml/"))]
    )

    with open(
        path.join(tmp_doc_path, "doc/_build/docfx_yaml/toc.yml"), "r"
    ) as file_handler:
        root_toc = yaml.safe_load(file_handler)

    root_package_item = [
        item
        for item in root_toc[0]["items"]
        if item["name"] == "azure.mgmt.containerservice"
    ]
    assert len(root_package_item) == 1
    aio_item = [
        item
        for item in root_package_item[0]["items"]
        if item["name"] == "azure.mgmt.containerservice.aio"
    ]
    v2017_07_01_item = [
        item
        for item in root_package_item[0]["items"]
        if item["name"] == "azure.mgmt.containerservice.v2017_07_01"
    ]
    v2018_03_31_item = [
        item
        for item in root_package_item[0]["items"]
        if item["name"] == "azure.mgmt.containerservice.v2018_03_31"
    ]
    assert len(aio_item) == 1
    assert len(v2017_07_01_item) == 1
    assert len(v2018_03_31_item) == 1
