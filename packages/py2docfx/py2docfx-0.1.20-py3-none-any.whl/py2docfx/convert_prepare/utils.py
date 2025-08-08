import os
import shutil
import stat

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

def remove_folder(folder: str | os.PathLike) -> None:
    try:
        shutil.rmtree(folder)
    except PermissionError as e:
        if '.git' and '.idx' in str(e):
            shutil.rmtree(folder, ignore_errors=False, onerror=on_rm_error)
        if os.path.exists(folder):
            raise RuntimeError(f"Failed to remove folder {folder}")

def temp_folder_clean_up(folder_list: list[str | os.PathLike]) -> None:
    for folder in folder_list:
        if os.path.exists(folder):
            remove_folder(folder)
            
def prepare_out_dir(output_root: str | os.PathLike) -> os.PathLike | None:
    # prepare output_root\DOC_FOLDER_NAME (if folder contains files, raise exception)
    if output_root:
        if os.path.exists(output_root):
            if os.path.isfile(output_root):
                raise ValueError(f"""output-root-folder is a path of file,
                                    output-root-folder value: {output_root}""")
            else:
                if len(os.listdir(output_root)) > 0:
                    raise ValueError(f"""output-root-folder isn't empty,
                                    output-root-folder value: {output_root}""")
                return output_root
        else:
            os.makedirs(output_root)
            return output_root
    else:
        return None