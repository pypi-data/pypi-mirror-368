import sys
import yaml
from yaml import safe_load

PACKAGES = "packages"


def merge_root_package(root_package_yaml_path, subpackages):
    with open(root_package_yaml_path, "r", encoding="utf-8") as file_handler:
        mime_header = file_handler.readline()
        root_package_data = safe_load(file_handler)

    root_package_data[PACKAGES] = []

    for subpackage in subpackages:
        if subpackage not in root_package_data[PACKAGES]:
            root_package_data[PACKAGES].append(subpackage)

    yaml_content = yaml.dump(
        root_package_data, default_flow_style=False, indent=2, sort_keys=False
    )
    with open(root_package_yaml_path, "w", encoding="utf-8") as file_handler:
        file_handler.write(mime_header + yaml_content)


def main():
    root_package_yaml_path = sys.argv[1]
    subpackages = sys.argv[2:]
    print("------Start to merge subpackages------")
    merge_root_package(root_package_yaml_path, subpackages)

if __name__ == "__main__":
    main()
    