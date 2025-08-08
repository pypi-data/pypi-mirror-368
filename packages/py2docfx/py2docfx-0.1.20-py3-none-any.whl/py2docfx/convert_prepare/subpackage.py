import glob
import os
from os import path, scandir
import shutil
import yaml
from yaml import safe_load
from py2docfx.convert_prepare.subpackage_merge.merge_root_package import merge_root_package
from py2docfx.convert_prepare.subpackage_merge.merge_toc import merge_to_root_toc


def get_subpackages(source_folder, package_name) -> list[str]:
    """
    If subpackages don't depend on each other, running sphinx-build separately is faster
    Get subpackages for distribute RST files to subfolder

    input: [azure/mgmt/containerservice/aio/**, azure/mgmt/containerservice/v2017_07_01/**,
    azure/mgmt/containerservice/v2018_03_31/**, azure/mgmt/containerservice/__pycache__/**,
    azure/mgmt/containerservice/__init__.py]

    output: [aio, v2017_07_01, v2018_03_31]
    """

    package_root = path.join(
        source_folder, package_name.replace("-", "/")
    )  # azure-mgmt-network -> azure/mgmt/network
    return [
        f.name for f in scandir(package_root) if f.is_dir() and f.name != "__pycache__"
    ]


def move_rst_files_to_subfolder(rst_folder, package_name, subpackage_names) -> dict:
    """
    If subpackages don't depend on each other, running sphinx-build separately is faster
    Distribute RST files to subfolder

    folder_structure_before: 
    [azure.mgmt.containerservice.rst,
    azure.mgmt.containerservice.v2017_07_01.rst,
    azure.mgmt.containerservice.v2017_07_01.models.rst,
    azure.mgmt.containerservice.v2018_03_31.rst]

    folder_structure_after: 
    [azure.mgmt.containerservice.rst,
    v2017_07_01/azure.mgmt.containerservice.v2017_07_01.rst,
    v2017_07_01/azure.mgmt.containerservice.v2017_07_01.models.rst, 
    v2018_03_31/azure.mgmt.containerservice.v2018_03_31.rst]
    """

    rst_files = set(glob.glob("*.rst", root_dir=rst_folder))
    package_name_prefix = package_name.replace("-", ".") + "."
    subpackages_path = path.join(rst_folder, "subpackages")

    if path.exists(subpackages_path):
        shutil.rmtree(subpackages_path)
    os.mkdir(subpackages_path)

    subpackages_path_record = {}
    for subpackage_name in subpackage_names:
        subpackage_name_prefix = package_name_prefix + subpackage_name + "."
        current_subpackage_path = path.join(subpackages_path, subpackage_name)

        if path.exists(current_subpackage_path):
            shutil.rmtree(current_subpackage_path)
        os.mkdir(current_subpackage_path)

        subpackage_rst_files = set()
        for rst_file in rst_files:
            if rst_file.startswith(subpackage_name_prefix):
                shutil.move(
                    path.join(rst_folder, rst_file),
                    path.join(current_subpackage_path, rst_file),
                )
                subpackage_rst_files.add(rst_file)

        rst_files -= subpackage_rst_files
        subpackages_path_record[subpackage_name] = current_subpackage_path

        with open(os.path.join(current_subpackage_path, "index.rst"), "w", encoding="utf-8"):
            pass

    return subpackages_path_record


TOC_SUBPATH = "docfx_yaml/toc.yml"

INDEX_SUBPATH = "docfx_yaml/index.yml"

YAML_SUBPATH = "docfx_yaml/"

def merge_subpackage_files(subpackages_path_record, root_doc_path, package_name):
    package_name_prefix = package_name.replace("-", ".")

    root_package_yaml = f"{root_doc_path}/docfx_yaml/{package_name_prefix}.yml"

    root_toc_path = path.join(root_doc_path, TOC_SUBPATH)

    # TOC
    with open(root_toc_path, "r", encoding="utf-8") as file_handler:
        root_toc = safe_load(file_handler)

    for subpackage_name, subpackage_doc_path in subpackages_path_record.items():
        subpackage_toc_path = path.join(subpackage_doc_path, TOC_SUBPATH)
        subpackage_index_path = path.join(subpackage_doc_path, INDEX_SUBPATH)
        subpackage_fullname = f"{package_name_prefix}.{subpackage_name}"

        if path.exists(subpackage_toc_path):
            with open(subpackage_toc_path, "r", encoding="utf-8") as file_handler:
                subpackage_toc = safe_load(file_handler)

            root_toc = merge_to_root_toc(
                root_toc, subpackage_toc, package_name_prefix, subpackage_fullname
            )
            os.remove(subpackage_toc_path)

        # remove index.yml, it's not needed
        if path.exists(subpackage_index_path):
            os.remove(subpackage_index_path)

        # Move document yamls to root yaml folder
        for document_file in scandir(path.join(subpackage_doc_path, YAML_SUBPATH)):
            shutil.move(
                path.join(subpackage_doc_path, YAML_SUBPATH, document_file.name),
                path.join(root_doc_path, YAML_SUBPATH),
            )

    root_toc_content = yaml.dump(
        root_toc, default_flow_style=False, indent=2, sort_keys=False
    )
    with open(root_toc_path, "w", encoding="utf-8") as file_handler:
        file_handler.write(root_toc_content)

    # root package yaml
    merge_root_package(
        root_package_yaml,
        [package_name_prefix + "." + p for p in subpackages_path_record.keys()],
    )
