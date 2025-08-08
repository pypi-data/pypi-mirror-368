import os
import shutil

from py2docfx.convert_prepare.post_process.merge_toc import merge_toc

def test_merge_toc(tmp_path):
    shutil.copytree("convert_prepare/tests/data/post_process_merge_toc",
                    os.path.join(tmp_path, "post_process_merge_toc"))
    root_toc_path = os.path.join(tmp_path, "post_process_merge_toc/root_toc")
    package_toc_path = os.path.join(tmp_path, "post_process_merge_toc/package_toc")
    toc_assert_path = os.path.join(tmp_path, "post_process_merge_toc/toc_assert")
    merge_toc(root_toc_path, package_toc_path)

    with open(os.path.join(root_toc_path, "toc.yml"), "r", encoding="utf-8") as final_toc:
        toc_content = final_toc.read()

    with open(os.path.join(toc_assert_path, "toc.yml"), "r", encoding="utf-8") as assert_file:
        assert_toc = assert_file.read()

    assert toc_content == assert_toc
