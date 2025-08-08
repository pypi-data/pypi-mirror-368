from __future__ import annotations # Avoid A | B annotation break under <= py3.9
import asyncio
import logging
import os
import sys

from py2docfx import PACKAGE_ROOT
from py2docfx.convert_prepare.arg_parser import parse_command_line_args
from py2docfx.convert_prepare.constants import SOURCE_REPO, TARGET_REPO, DIST_TEMP, LOG_FOLDER
from py2docfx.convert_prepare.generate_document import generate_document
from py2docfx.convert_prepare.get_source import YAML_OUTPUT_ROOT
from py2docfx.convert_prepare.post_process.merge_toc import merge_toc, move_root_toc_to_target
from py2docfx.convert_prepare.package_info import PackageInfo
from py2docfx.convert_prepare.utils import temp_folder_clean_up, prepare_out_dir
import py2docfx.convert_prepare.environment as py2docfxEnvironment
import py2docfx.docfx_yaml.logger as py2docfxLogger

os.chdir(PACKAGE_ROOT)

async def donwload_package_generate_documents(
        package_info_list: list[PackageInfo],
        output_root: str | os.PathLike | None,
        output_doc_folder: os.PathLike | None,
        github_token: str, ado_token: str, required_package_list: list):
    
    start_num = len(required_package_list)
    env_prepare_tasks = []
    env_remove_tasks = []

    for idx in range(min([py2docfxEnvironment.VENV_BUFFER, len(package_info_list)])):
        package_info = package_info_list[idx]
        package_number = start_num + idx
        env_prepare_tasks.append(
            asyncio.create_task(py2docfxEnvironment.prepare_venv(idx, package_info, package_number, github_token, ado_token)))
    await asyncio.create_task(
            py2docfxEnvironment.prepare_base_venv(required_package_list, github_token, ado_token))

    for idx, package in enumerate(package_info_list):
        package_number = start_num + idx
        py2docfx_logger = py2docfxLogger.get_logger(__name__)
        msg = f"Processing package {package.name}, env_prepare_tasks: {len(env_prepare_tasks)}"
        py2docfx_logger.info(msg)

        try:
            await env_prepare_tasks[idx]
        except Exception as e:
            msg = f"Failed to setup venv for package {package.name}: {e}"
            py2docfx_logger.error(msg)
            raise e

        await generate_document(package, output_root,
                          py2docfxEnvironment.get_base_venv_sphinx_build_path(),
                          py2docfxEnvironment.get_venv_package_path(idx),
                          py2docfxEnvironment.get_base_venv_exe())

        merge_toc(YAML_OUTPUT_ROOT, package.path.yaml_output_folder)

        if output_doc_folder:
            package.path.move_document_to_target(os.path.join(output_doc_folder, package.name))

        if idx + py2docfxEnvironment.VENV_BUFFER < len(package_info_list):
            buffer_package_idx = idx + py2docfxEnvironment.VENV_BUFFER
            
            msg = f"Creating venv {buffer_package_idx}"
            py2docfx_logger.info(msg)
            
            env_prepare_tasks.append(
                asyncio.create_task(py2docfxEnvironment.prepare_venv(buffer_package_idx, 
                                                                     package_info_list[buffer_package_idx], 
                                                                     start_num + buffer_package_idx, 
                                                                     github_token, 
                                                                     ado_token)))

        if idx >= 1:
            env_remove_tasks.append(asyncio.create_task(
                py2docfxEnvironment.remove_environment(idx-1)))

        if idx > py2docfxEnvironment.VENV_BUFFER and env_remove_tasks[idx-py2docfxEnvironment.VENV_BUFFER] != None:
            msg = f"Removing venv {idx-py2docfxEnvironment.VENV_BUFFER}"
            py2docfx_logger.info(msg)
            await env_remove_tasks[idx-py2docfxEnvironment.VENV_BUFFER]
    
    if output_doc_folder:
        move_root_toc_to_target(YAML_OUTPUT_ROOT, output_doc_folder)
    
    for idx in range(len(env_remove_tasks)):
        if env_remove_tasks[idx] != None and not env_remove_tasks[idx].done():
            await env_remove_tasks[idx]

def fishish_up():
    warning_count, error_count = py2docfxLogger.get_warning_error_count()
    py2docfxLogger.output_log_by_log_level()
    print(f"Warning count: {warning_count}, Error count: {error_count}")
    logging.shutdown()
    
async def main(argv) -> int:
    # TODO: may need to purge pip cache
    (package_info_list,
     required_package_list,
     github_token, ado_token,
     output_root, verbose,
     show_warning) = parse_command_line_args(argv)

    clean_up_folder_list = [py2docfxEnvironment.VENV_DIR, DIST_TEMP, SOURCE_REPO, TARGET_REPO, LOG_FOLDER]
    temp_folder_clean_up(clean_up_folder_list)
    
    # create log folder and package log folder
    log_folder = os.path.join(PACKAGE_ROOT, LOG_FOLDER)
    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(os.path.join(log_folder, "package_logs"), exist_ok=True)
    
    py2docfxLogger.decide_global_log_level(verbose, show_warning)
    
    py2docfx_logger = py2docfxLogger.get_logger(__name__)

    msg = "Adding yaml extension to path"
    py2docfx_logger.info(msg)
    
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),'docfx_yaml'))
    output_doc_folder = prepare_out_dir(output_root)

    try:
        await donwload_package_generate_documents(
            package_info_list, output_root, output_doc_folder,
            github_token, ado_token, required_package_list)
    except Exception as e:
        msg = f"An error occurred: {e}"
        py2docfx_logger.error(msg)
        fishish_up()
        asyncio.get_event_loop().stop()
        raise
    
    fishish_up()
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:])))
