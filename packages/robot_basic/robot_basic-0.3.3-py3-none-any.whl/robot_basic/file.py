import fnmatch
import os.path
import pathlib
import shutil
import tempfile
import time
from collections import namedtuple

from robot_base import log_decorator, ParamException


@log_decorator
def get_file_list(
    directory,
    match_patten,
    find_all=False,
    ignore_hidden=False,
    sort_by=False,
    sort_strategy="name",
    sort_type="asc",
    **kwargs,
):
    if not os.path.exists(directory):
        return []
    file_list = []
    if find_all:
        for root, dirs, files in os.walk(directory):
            for name in files:
                if fnmatch.fnmatch(name, match_patten):
                    if ignore_hidden and name.startswith("."):
                        continue
                    file_list.append(os.path.join(root, name))
    else:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and fnmatch.fnmatch(entry.name, match_patten):
                    if ignore_hidden and entry.name.startswith("."):
                        continue
                    file_list.append(entry.name)

    if sort_by:
        if sort_strategy == "name":
            file_list.sort(key=lambda x: x)
            if sort_type == "desc":
                file_list.reverse()
        elif sort_strategy == "size":
            file_list.sort(key=lambda x: os.path.getsize(x))
            if sort_type == "desc":
                file_list.reverse()
        elif sort_strategy == "create_time":
            file_list.sort(key=lambda x: os.path.getctime(x))
            if sort_type == "desc":
                file_list.reverse()
        elif sort_strategy == "modify_time":
            file_list.sort(key=lambda x: os.path.getmtime(x))
            if sort_type == "desc":
                file_list.reverse()
    return file_list


@log_decorator
def write_file(file_path, content, encoding="utf-8", append=False, **kwargs):
    with open(file_path, "a" if append else "w", encoding=encoding) as f:
        f.write(content)


@log_decorator
def read_file(file_path, read_type, encoding="utf-8", **kwargs):
    if not os.path.exists(file_path):
        raise ParamException(f"{file_path}文件不存在")
    if read_type == "bytes":
        with open("example.bin", "rb") as file:
            # 读取文件内容
            return file.read()
    with open(file_path, "r", encoding=encoding) as f:
        if read_type == "lines":
            return f.readlines()
        elif read_type == "content":
            return f.read()


@log_decorator
def delete_file(file_path, **kwargs):
    if os.path.exists(file_path):
        os.remove(file_path)


@log_decorator
def copy_file(src_path, dst_directory_path, overwrite_type="overwrite", **kwargs):
    if not os.path.exists(src_path):
        raise ParamException(f"{src_path}文件不存在")
    dst_path = os.path.join(dst_directory_path, os.path.basename(src_path))
    if os.path.exists(dst_path):
        if overwrite_type == "overwrite":
            os.remove(dst_path)
        elif overwrite_type == "skip":
            return
        elif overwrite_type == "rename":
            while os.path.exists(dst_path):
                dst_path = os.path.join(
                    os.path.dirname(dst_path), os.path.basename(dst_path) + "_copy"
                )
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy(src_path, dst_path)
    return dst_path


@log_decorator
def move_file(src_path, dst_directory_path, overwrite_type="overwrite", **kwargs):
    if not os.path.exists(src_path):
        raise ParamException(f"{src_path}文件不存在")
    dst_path = os.path.join(dst_directory_path, os.path.basename(src_path))
    if os.path.exists(dst_path):
        if overwrite_type == "overwrite":
            os.remove(dst_path)
        elif overwrite_type == "skip":
            return
    os.makedirs(os.path.dirname(dst_path))
    shutil.move(src_path, dst_path)
    return dst_path


@log_decorator
def rename_file(src_path, new_filename, overwrite_type="overwrite", **kwargs):
    if not os.path.exists(src_path):
        raise ParamException(f"{src_path}文件不存在")
    dst_path = os.path.join(os.path.dirname(src_path), new_filename)
    if os.path.exists(dst_path):
        if overwrite_type == "overwrite":
            os.remove(dst_path)
        elif overwrite_type == "skip":
            return
    shutil.move(src_path, dst_path)
    return dst_path


@log_decorator
def get_path_info(src_path, **kwargs):
    if not os.path.exists(src_path):
        raise ParamException(f"{src_path}文件不存在")
    file_path = pathlib.Path(src_path)
    # 获取文件的根目录
    root_dir = file_path.drive
    # 获取文件的父目录
    parent_dir = file_path.parent
    # 获取文件名（包括扩展名）
    file_name = file_path.name
    # 获取基本文件名（不包括扩展名）
    file_base_name = file_path.stem
    # 获取文件扩展名（包括点）
    file_extension = file_path.suffix
    FileParts = namedtuple(
        "FileParts",
        ["root_dir", "parent_dir", "file_name", "file_base_name", "file_extension"],
    )
    return FileParts(root_dir, parent_dir, file_name, file_base_name, file_extension)


@log_decorator
def wait_file_status(file_path, wait_type, timeout, **kwargs):
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        if os.path.exists(file_path) and wait_type == "create":
            return True
        elif not os.path.exists(file_path) and wait_type == "delete":
            return True
        time.sleep(0.1)


@log_decorator
def get_directory_list(directory, match_patten, find_child=False, **kwargs):
    if not os.path.exists(directory):
        return []
    directory_list = []
    if not find_child:
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir() and fnmatch.fnmatch(entry.name, match_patten):
                    directory_list.append(entry.name)
    else:
        for root, dirs, files in os.walk(directory):
            for name in dirs:
                if fnmatch.fnmatch(name, match_patten):
                    directory_list.append(os.path.join(root, name))
    return directory_list


@log_decorator
def create_directory(parent_directory, directory_name, **kwargs):
    os.makedirs(os.path.join(parent_directory, directory_name), exist_ok=True)


@log_decorator
def delete_directory(directory, **kwargs):
    shutil.rmtree(directory)


@log_decorator
def clear_directory(directory, **kwargs):
    if not os.path.exists(directory):
        raise ParamException(f"{directory}目录不存在")

    for root, dirs, files in os.walk(directory):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))


@log_decorator
def copy_directory(src_directory, dst_directory, overwrite_type="overwrite", **kwargs):
    if not os.path.exists(src_directory):
        raise ParamException(f"{src_directory}目录不存在")
    if os.path.exists(dst_directory):
        if overwrite_type == "overwrite":
            shutil.rmtree(dst_directory)
        elif overwrite_type == "skip":
            return
        elif overwrite_type == "rename":
            while os.path.exists(dst_directory):
                dst_directory = os.path.join(
                    os.path.dirname(dst_directory),
                    os.path.basename(dst_directory) + "_copy",
                )
    shutil.copy(src_directory, dst_directory)
    return dst_directory


@log_decorator
def move_directory(src_directory, dst_directory, overwrite_type="overwrite", **kwargs):
    if not os.path.exists(src_directory):
        raise ParamException(f"{src_directory}目录不存在")
    if os.path.exists(dst_directory):
        if overwrite_type == "overwrite":
            shutil.rmtree(dst_directory)
        elif overwrite_type == "skip":
            return
        elif overwrite_type == "rename":
            while os.path.exists(dst_directory):
                dst_directory = os.path.join(
                    os.path.dirname(dst_directory),
                    os.path.basename(dst_directory) + "_copy",
                )
    shutil.move(src_directory, dst_directory)
    return dst_directory


@log_decorator
def rename_directory(
    src_directory, new_directory_name, overwrite_type="overwrite", **kwargs
):
    if not os.path.exists(src_directory):
        raise ParamException(f"{src_directory}目录不存在")
    dst_directory = os.path.join(os.path.dirname(src_directory), new_directory_name)
    if os.path.exists(dst_directory):
        if overwrite_type == "overwrite":
            shutil.rmtree(dst_directory)
        elif overwrite_type == "skip":
            return
        elif overwrite_type == "rename":
            while os.path.exists(dst_directory):
                dst_directory = os.path.join(
                    os.path.dirname(dst_directory),
                    os.path.basename(dst_directory) + "_copy",
                )
    shutil.move(src_directory, dst_directory)
    return dst_directory


@log_decorator
def get_system_directory(directory_type, **kwargs):
    if directory_type == "temp":
        return tempfile.gettempdir()
    elif directory_type == "user":
        return os.path.expanduser("~")
    elif directory_type == "current":
        return os.getcwd()
    elif directory_type == "desktop":
        return os.path.join(os.path.expanduser("~"), "Desktop")
    elif directory_type == "documents":
        return os.path.join(os.path.expanduser("~"), "Documents")
    elif directory_type == "downloads":
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif directory_type == "music":
        return os.path.join(os.path.expanduser("~"), "Music")
    elif directory_type == "pictures":
        return os.path.join(os.path.expanduser("~"), "Pictures")
    elif directory_type == "videos":
        return os.path.join(os.path.expanduser("~"), "Videos")
    elif directory_type == "program_files":
        return os.environ["ProgramFiles"]
    elif directory_type == "program_files_x86":
        return os.environ["ProgramFiles(x86)"]
    elif directory_type == "program_data":
        return os.environ["ProgramData"]
    elif directory_type == "local_app_data":
        return os.environ["LocalAppData"]
    elif directory_type == "app_data":
        return os.environ["AppData"]
    elif directory_type == "system_drive":
        return os.environ["SystemDrive"]
    elif directory_type == "system_root":
        return os.environ["SystemRoot"]
