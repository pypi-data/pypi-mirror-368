import sys
import yaml
from yaml import safe_load


def merge_to_root_toc(root_toc, sub_package_toc, package_name_prefix, sub_package_name):
    sub_package_toc_actual = None
    toc_item_node = None
    for sub_node in sub_package_toc[0]["items"]:
        if sub_node["name"] == sub_package_name:
            sub_package_toc_actual = sub_node
            break

    for toc_nodes in root_toc[0]["items"]:
        if toc_nodes["name"] == package_name_prefix:
            toc_item_node = toc_nodes
            break

    if not sub_package_toc_actual:
        raise ValueError(
            f"Can't find toc node matching sub package name: {sub_package_name}."
        )

    if not toc_item_node:
        raise ValueError("Can't find toc node matching root package name.")

    toc_item_node["items"].append(sub_package_toc_actual)
    return root_toc


def main():
    root_toc_yaml_path = sys.argv[1]
    subpackage_toc_yaml_path = sys.argv[2]
    package_name_prefix = sys.argv[3]
    sub_package_name = sys.argv[4]

    with open(root_toc_yaml_path, "r", encoding="utf-8") as file_handler:
        root_toc = safe_load(file_handler)

    with open(subpackage_toc_yaml_path, "r", encoding="utf-8") as file_handler:
        sub_package_toc = safe_load(file_handler)

    root_toc = merge_to_root_toc(
        root_toc, sub_package_toc, package_name_prefix, sub_package_name
    )
    root_toc_content = yaml.dump(
        root_toc, default_flow_style=False, indent=2, sort_keys=False
    )
    with open(root_toc_yaml_path, "w", encoding="utf-8") as file_handler:
        file_handler.write(root_toc_content)

if __name__ == "__main__":
    main()
    