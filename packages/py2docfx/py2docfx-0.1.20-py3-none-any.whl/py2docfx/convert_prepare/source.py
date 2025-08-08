import glob
import os.path as path
import os
import shutil

def make_dir(path_str):
    if not path.exists(path_str):
        os.makedirs(path_str)

class Source:
    def __init__(self, source_folder, yaml_output_folder, package_name):
        self.source_folder = source_folder
        self.yaml_output_folder = yaml_output_folder # "target_repo"/"docs-ref-autogen"/pkg.name
        make_dir(self.yaml_output_folder)
        self.package_name = package_name
        self.doc_folder = path.join(self.source_folder, "doc")
        make_dir(self.doc_folder)

    def create_doc_folder(self):
        if not path.exists(self.doc_folder):
            os.mkdir(self.doc_folder)

    def remove_all_rst(self):
        for rst_path in glob.iglob(os.path.join(self.doc_folder, '*.rst')):
            os.remove(rst_path)

    def copy_manual_rst(self, manual_rst_folder) -> bool:
        has_manual_rst = False
        if os.path.exists(manual_rst_folder):
            for file in os.listdir(manual_rst_folder):
                if file.endswith(".rst"):
                    shutil.copy(os.path.join(manual_rst_folder, file), self.doc_folder)
                    has_manual_rst = True
        return has_manual_rst

    def move_document_to_target(self, target_doc_folder):
        yaml_output_folder = path.join(self.yaml_output_folder, "_build", "docfx_yaml")
        if os.path.exists(target_doc_folder) and os.path.isdir(target_doc_folder):
            # avoid outputing duplicate packages. shutil.move will include the src parent folder 
            # if target folder exists
            return
        else:
            shutil.move(yaml_output_folder, target_doc_folder)
