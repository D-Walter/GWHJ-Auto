import json
import os
from typing import Generator

from media_wiki_manager import MediaWikiManager

with open("settings.json", 'r', encoding='utf8', newline='') as fs:
    settings = json.load(fs)

known_dict_path = os.path.join(settings['local_wiki_root_path'], 'dict.json')
if os.path.exists(known_dict_path):
    with open(known_dict_path, 'r', encoding='utf8',
              newline='') as F:
        known_dict = json.load(F)

huiji_manager: MediaWikiManager = MediaWikiManager(settings['huiji_account'], settings['huiji_password'],
                                                   settings['huiji_host'])


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
