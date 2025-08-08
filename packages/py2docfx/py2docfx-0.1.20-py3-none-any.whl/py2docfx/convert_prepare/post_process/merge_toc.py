from __future__ import annotations # Avoid A | B annotation break under <= py3.9
import os
import shutil

from py2docfx.docfx_yaml.logger import get_logger

TOC_FILE_PATH = "toc.yml"
PACKAGE_TOC_FILE_PATH = "_build/docfx_yaml/toc.yml"
def merge_toc(
        root_doc_path: str | os.PathLike, package_doc_path: str | os.PathLike):
    py2docfx_logger = get_logger(__name__)
    root_toc_path = os.path.join(root_doc_path, TOC_FILE_PATH)
    package_toc_path = os.path.join(package_doc_path, PACKAGE_TOC_FILE_PATH)

    with open(package_toc_path, "r", encoding="utf-8") as file_handle:
        toc_content = file_handle.read()

    if len(toc_content) > 0 and toc_content.strip() != "[]":
        with open(root_toc_path, "a", encoding="utf-8") as root_toc_handle:
            root_toc_handle.write(toc_content)
            if not toc_content.endswith("\n"):
                root_toc_handle.write("\n")
    else:
        msg = f"TOC content empty: {package_toc_path}"
        py2docfx_logger.error(msg)
        raise ValueError(msg)

    # delete package toc.yml
    os.remove(package_toc_path)

def move_root_toc_to_target(root_doc_path: str| os.PathLike, target_doc_folder):
    shutil.move(os.path.join(root_doc_path, TOC_FILE_PATH), target_doc_folder)
