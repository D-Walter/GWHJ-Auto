import os
from mwclient.page import Page
import global_utils


def arena_get_page_mounts(force_refresh=False) -> (int, list):
    return arena_download_all_pages_in_categories(['Griffon skins',
                                                   'Jackal skin',
                                                   'Jackal skins',
                                                   'Raptor skins',
                                                   'Roller Beetle skins',
                                                   'Skimmer skins',
                                                   'Skyscale skins',
                                                   'Springer skins',
                                                   'Warclaw skins',
                                                   'Gem Store mounts'], os.path.join("wikiText", "en", "mounts"),
                                                  force_refresh)


def arena_get_mount_licenses(force_refresh=False) -> (int, list):
    return arena_download_all_pages_in_categories(['Gem Store mount licenses'],
                                                  os.path.join("wikiText", "en", "mount licenses"),
                                                  force_refresh)


def arena_get_items(force_refresh=False) -> (int, list):
    return arena_download_all_pages_in_categories(["items"], os.path.join("wikiText", "en", "items"), force_refresh)


def arena_get_pages_embedded_with(embedded_page_name: str, to_folder: str):
    pages = global_utils.arena_manager.get_page(embedded_page_name).embeddedin(namespace=0)  # 15509
    arena_download_all_pages(pages, os.path.join(global_utils.settings["local_wiki_root_path"], to_folder))


# 将列表categories下所有页面下载到to_folder路径，请注意，to_folder路径是以global_utils.settings["local_wiki_root_path"]为根目录的相对路径
# categories会被各自写入与to_folder最低级路径相同名的txt文件中。若文件已存在，则会尝试读取该文件，只有当force_refresh_list为True时才会忽视本地文件重新下载
# 返回一个(int,list)元组，分别对应成功页面数和失败页面名列表
def arena_download_all_pages_in_categories(categories: list, to_folder: str, force_refresh_list: bool = False) -> (
        int, list):
    tgt_folder = os.path.join(global_utils.settings["local_wiki_root_path"], to_folder)
    list_local_file = os.path.join(tgt_folder, f"{to_folder.split(os.sep)[-1]}.txt")
    pages_not_exist = []
    if force_refresh_list or not os.path.exists(list_local_file):
        if not os.path.exists(tgt_folder):
            os.makedirs(tgt_folder)
        with open(list_local_file, 'w+', encoding='utf8') as F:
            for page in global_utils.arena_manager.get_elements_in_categories(categories):
                F.write(f"{page.name}\n")
                F.flush()
                if not page.exists:
                    pages_not_exist.append(page.name)
                    continue
                if not arena_download_single_page(page, tgt_folder):
                    pages_not_exist.append(page.name)
                    continue
    else:
        with open(list_local_file, 'r', encoding='utf8') as F:
            while F.readable():
                line_content = F.readline()
                page = global_utils.arena_manager.get_page(line_content)
                if not page.exists:
                    pages_not_exist.append(page.name)
                    continue
                if not arena_download_single_page(page, tgt_folder):
                    pages_not_exist.append(page.name)
                    continue


def arena_download_all_pages(pages: list, to_folder: str) -> (int, list):
    if not os.path.exists(to_folder):
        os.makedirs(to_folder, 775)
    page_counter = 0
    pages_not_exist = []
    for page in pages:
        p = global_utils.arena_manager.get_page(page)
        file = os.path.join(to_folder, global_utils.ascii_name(f"{global_utils.standardize_name(p.name)}.wiki"))
        print(file)
        if not p.exists:
            pages_not_exist.append(p.name)
            continue
        if os.path.exists(file):
            os.remove(file)
        with open(file, 'w+', encoding='utf8') as F:
            F.write(p.text())
        page_counter += 1
    return page_counter, pages_not_exist


def arena_download_single_page(page: Page, to_folder: str) -> bool:
    file = os.path.join(to_folder,
                        global_utils.ascii_name(f"{global_utils.standardize_name(page.name)}.wiki"))
    if not page.exists:
        return False
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w+', encoding='utf8') as f:
        f.write(page.text())
    return True
