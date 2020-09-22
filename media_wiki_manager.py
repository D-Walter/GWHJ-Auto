import os
import re
import threading
import time
from time import sleep
from typing import Generator
from mwclient import Site, listing, page
from mwclient.page import Page
import global_utils


class MediaWikiManager:
    __account: str = None
    __password: str = None
    __site_service: Site = None
    __operation_index: int = 0
    __operation_mutex = threading.Lock()
    __access_limitation: int = 5
    __access_limitation_counter = 0
    __access_limitation_duration = 3
    __access_mutex = threading.Lock()

    @staticmethod
    def download_single_page(tgt_page: Page, to_folder: str) -> bool:
        file = os.path.join(to_folder,
                            global_utils.get_ascii_name(f"{global_utils.get_standardized_name(tgt_page.name)}.wiki"))
        print(file)
        if not tgt_page.exists:
            return False
        if not os.path.exists(to_folder):
            os.makedirs(to_folder)
        if os.path.exists(file):
            os.remove(file)
        with open(file, 'w+', encoding='utf8') as f:
            f.write(tgt_page.text())
        return True

    # 将列表categories下所有页面下载到to_folder路径，请注意，to_folder路径是以global_utils.settings["local_wiki_root_path"]为根目录的相对路径
    # categories会被各自写入与to_folder最低级路径相同名的txt文件中。若文件已存在，则会尝试读取该文件，只有当force_refresh_list为True时才会忽视本地文件重新下载
    # 返回一个(int,list)元组，分别对应成功页面数和失败页面名列表
    def download_all_pages_in_categories(self, categories: list, to_folder: str, force_refresh_list: bool = False) -> (
            int, list):
        tgt_folder = os.path.join(to_folder)
        list_local_file = os.path.join(tgt_folder, f"{to_folder.split(os.sep)[-1]}.txt")
        pages_not_exist = []
        if force_refresh_list or not os.path.exists(list_local_file):
            if not os.path.exists(tgt_folder):
                os.makedirs(tgt_folder)
            with open(list_local_file, 'w+', encoding='utf8') as F:
                for _page in self.get_elements_in_categories(categories):
                    F.write(f"{_page.name}\n")
                    F.flush()
                    if not self.download_single_page(_page, tgt_folder):
                        pages_not_exist.append(_page.name)
                        continue
        else:
            with open(list_local_file, 'r', encoding='utf8') as F:
                while F.readable():
                    line_content = F.readline()
                    _page = global_utils.arena_manager.get_page(line_content)
                    if not self.download_single_page(_page, tgt_folder):
                        pages_not_exist.append(_page.name)
                        continue

    def download_all_pages(self, pages_names: list, to_folder: str) -> (int, list):
        if not os.path.exists(to_folder):
            os.makedirs(to_folder, 775)
        page_counter = 0
        pages_not_exist = []
        for page_name in pages_names:
            p = self.get_page(page_name)
            file = os.path.join(to_folder,
                                global_utils.get_ascii_name(f"{global_utils.get_standardized_name(p.name)}.wiki"))
            if MediaWikiManager.download_single_page(p, file):
                page_counter += 1
            else:
                pages_not_exist.append(page_name)
        return page_counter, pages_not_exist

    def get_elements_in_categories(self, categories_names: list, sender="UNKNOWN") -> Generator:
        my_operation_index = self.__ask_for_operation_index__()
        site_service = self.__get_site_service__(f'OPERATION[ERGODIC-CAT] from USER[{sender}]', False)
        c_list = categories_names[:]
        while len(c_list) >= 1:
            self.__ask_for_access__()
            operation_details_text = f"OPERATION[GET] to CATEGORY[{c_list[0]}] from USER[{sender}](OI[{my_operation_index}])"
            try:
                category_pointer = site_service.categories[c_list[0]]
            except Exception as e:
                self.__write_log__(f"{operation_details_text} failed" + os.linesep + str(e))
                continue
            for obj in category_pointer:
                if isinstance(obj, listing.Category):
                    c_name = obj.name
                    c_name = c_name.replace('Category:', '')
                    c_list.append(c_name)
                elif isinstance(obj, page.Page):
                    name = obj.name
                    match = re.search(r'[tT]emplate:', name)
                    if not match:
                        yield obj
            c_list.pop(0)

    def update_page(self, page_name: str, content: str, summary: str = "BOT AUTO", sender="UNKNOWN") -> bool:
        return self.__operate_page__('UPDATE', page_name, content=content, summary=summary, sender=sender) is not None

    def get_page(self, page_name: str, sender="UNKNOWN") -> Page:
        return self.__operate_page__('GET', page_name, sender=sender)

    def save_new_page(self, page_name: str, content: str, summary: str = "BOT AUTO", sender="UNKNOWN") -> bool:
        return self.__operate_page__('CREATE', page_name, content=content, summary=summary, sender=sender) is not None

    def delete_page(self, page_name: str, reason: str = "BOT AUTO", sender="UNKNOWN") -> bool:
        return self.__operate_page__('DELETE', page_name, reason=reason, sender=sender) is not None

    def __get_cur_operation_index__(self) -> int:
        self.__operation_mutex.acquire()
        ret = self.__operation_index
        self.__operation_mutex.release()
        return ret

    def __ask_for_operation_index__(self) -> int:
        self.__operation_mutex.acquire()
        ret = self.__operation_index
        self.__operation_index += 1
        self.__operation_mutex.release()
        return ret

    def __get_access_rate__(self) -> str:
        self.__access_mutex.acquire()
        ret = self.__access_limitation_counter / self.__access_limitation_duration
        self.__access_mutex.release()
        return f"{self.__access_limitation_counter}/{self.__access_limitation_duration}:{ret}"

    def __ask_for_access__(self):
        self.__access_mutex.acquire()
        while (
                self.__access_limitation_counter / self.__access_limitation_duration) >= self.__access_limitation:
            sleep(0.02)
        self.__access_limitation_counter += 1
        self.__access_mutex.release()
        threading.Timer(self.__access_limitation_duration, self.__minus_access_counter__).start()

    def __minus_access_counter__(self):
        self.__access_mutex.acquire()
        self.__access_limitation_counter -= 1
        self.__access_mutex.release()

    def __write_log__(self, message):
        global_utils.write_log(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{'ONLINE' if self.__site_service.logged_in else 'OFFLINE'}]{message}")

    def __get_site_service__(self, sender='UNKNOWN', need_logged=True) -> Site:
        if need_logged and not self.__site_service.logged_in:
            self.__write_log__(f"{sender} asks for a new site service")
            self.__site_service.login(self.__account, self.__password)
            self.__write_log__(f"Logged in")
        return self.__site_service

    def __operate_page__(self, operation_type: str, page_name: str, content: str = None, summary: str = "BOT AUTO",
                         reason: str = "BOT AUTO",
                         retry_times: int = 10, retry_interval: int = 30, sender: str = "UNKNOWN") -> Page or None:
        my_operation_index = self.__ask_for_operation_index__()
        site_service = self.__get_site_service__(f'OPERATION[{operation_type}] from USER[{sender}]',
                                                 operation_type != 'GET')
        tgt_page = None

        def update_page():
            nonlocal tgt_page, page_name
            self.__ask_for_access__()
            tgt_page = site_service.pages[page_name]
            if not tgt_page.exists:
                tgt_page = None
                return f'Page "{page_name}" doesn\'t exist'
            else:
                tgt_page.save(content, summary=summary, bot=True)

        def get_page():
            nonlocal tgt_page, page_name
            self.__ask_for_access__()
            tgt_page = site_service.pages[page_name]

        def create_page():
            nonlocal tgt_page, page_name
            self.__ask_for_access__()
            tgt_page = site_service.pages[page_name]
            if tgt_page.exists:
                tgt_page = None
                return f'Duplicated page "{page_name}"'
            else:
                tgt_page.save(content, summary=summary, bot=True)

        def delete_page():
            nonlocal tgt_page, page_name
            self.__ask_for_access__()
            tgt_page = site_service.pages[page_name]
            if not tgt_page.exists:
                tgt_page = None
                return f'Page "{page_name}" doesn\'t exist'
            else:
                tgt_page.delete(reason=reason)

        def __try_doing__(func, retry=None) -> str or None:
            nonlocal retry_times, retry_interval
            success_flag = False
            retry_counter = 0
            while not success_flag:
                if retry_counter >= retry_times:
                    return f"More than {retry_times} times retrying"
                try:
                    ret = func()
                    if ret is not None:
                        return ret
                    success_flag = True
                except Exception as e:
                    retry_counter += 1
                    retry(e, retry_counter)
                    sleep(retry_interval)
            return None

        page_operations_funcs = {
            'GET': get_page,
            'CREATE': create_page,
            'DELETE': delete_page,
            'UPDATE': update_page
        }
        operation_details_text = f"OPERATION[{operation_type}] to PAGE[{page_name}] from USER[{sender}](OI[{my_operation_index}])"
        result = __try_doing__(page_operations_funcs[operation_type],
                               lambda e, c: self.__write_log__(
                                   f"{operation_details_text} failed, this is the {c}th failure(s)"
                                   + os.linesep + e))
        if result is None:
            self.__write_log__(
                f"{operation_details_text} completed")
        else:
            self.__write_log__(
                f"{operation_details_text} failed[{result}]")
        return tgt_page

    def __init__(self, account, password, host):
        self.__account = account
        self.__password = password
        self.__site_service = Site(host, path='/')
