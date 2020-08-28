import json
import os
import time
from typing import Generator

from media_wiki_manager import MediaWikiManager

with open("settings.json", 'r', encoding='utf8', newline='') as fs:
    settings = json.load(fs)

if not os.path.exists(settings["logs_folder_path"]):
    os.makedirs(settings["logs_folder_path"], 0x777)
logs_file_full_path = os.path.join(settings["logs_folder_path"], settings["logs_file_name"])

known_dicts_folder = os.path.join(settings['local_wiki_root_path'], 'dicts')
known_dict = {}
if os.path.exists(known_dicts_folder):
    for f in os.listdir(known_dicts_folder):
        if os.path.isfile(f):
            with open(known_dicts_folder, 'r', encoding='utf8',
                      newline='') as F:
                try:
                    t_dict = json.load(F)
                    known_dict.update(t_dict)
                except:
                    continue

huiji_manager: MediaWikiManager = MediaWikiManager(settings['huiji_account'], settings['huiji_password'],
                                                   settings['huiji_host'])
arena_manager: MediaWikiManager = MediaWikiManager(settings['arena_account'], settings['arena_password'],
                                                   settings['arena_host'])


# 将一个英文wiki界面名标准化至灰机wiki标准
def standardize_name(src_name: str) -> str:
    return os.path.split(src_name)[-1].replace('.wiki', '').replace("File:", "").replace('%22', '"'). \
        replace('%2F', "/").replace('%3A', ":").replace('%3F', "?").replace('%2A', "*")


# 快速组装多个中间文件夹，并且以全局设置作为根目录
def get_path(mid_folders: list) -> str:
    mid_folders[0:0] = [settings['local_wiki_root_path']]
    return os.path.sep.join(mid_folders)


# 迭代遍历root文件夹，返回文件路径生成器，该函数会无限深度遍历所有子文件夹，遍历顺序以字母顺序进行
def get_files_path(root: str, out: list, extension: str) -> Generator:
    try:
        for file in os.listdir(root):
            file_pointer = os.path.join(root, file)
            if os.path.isdir(file_pointer):
                get_files_path(file_pointer, out, extension)
            elif os.path.isfile(file_pointer) and os.path.splitext(file_pointer)[-1] == f'.{extension}':
                yield file_pointer
        return out
    except PermissionError:
        pass


# 遍历root文件夹，返回文件内容生成器，该函数会无限深度遍历所有子文件夹，遍历顺序以字母顺序进行
def get_wiki_files(root: str) -> Generator:
    if not os.path.isdir(root):
        yield None
    for file_path in get_files_path(root, [], "WIKI"):
        with open(file_path, 'r', encoding='utf8', newline='') as fs:
            yield fs.read(), '.'.split(os.path.split(file_path)[-1])[0]


def write_log(msg) -> None:
    with open(logs_file_full_path, 'a', encoding='utf-8') as fs:
        fs.write(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}]{msg}{os.linesep}")
        fs.flush()
