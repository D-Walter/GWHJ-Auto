import os
import re
import threading
import time
from time import sleep
from mwclient import Site, listing, page
from mwclient.page import Page


class MediaWikiManager:
    __account: str = None
    __password: str = None
    __site_service: Site = None
    __operation_index: int = 0
    __operation_index_limitation: int = 5
    __operation_index_mutex = threading.Lock()

    def get_items_in_category(self, in_category, sender="UNKNOWN"):
        MediaWikiManager.__try_doing__(self.__walk_category__,
                                       lambda: self.__write_log__(""))
        return self.__walk_category__(in_category, [])

    def __walk_category__(self, category_name: str, c_list: list) -> list:
        site_service = self.__get_site_service__(need_logged=False)
        try:
            temp_items = []
            for obj in site_service.categories[category_name]:
                if isinstance(obj, listing.Category):
                    c_name = obj.name
                    c_name = c_name.replace('Category:', '')
                    self.__walk_category__(c_name, c_list)
                elif isinstance(obj, page.Page):
                    name = obj.name
                    if name not in c_list:
                        match = re.search(r'[tT]emplate:', name)
                        if not match:
                            temp_items.append(name)
                            print('add page:', name)
            c_list[0:0] = temp_items
            return c_list
        except PermissionError:
            sleep(30)
            return []

    def get_page(self, page_name: str, sender="UNKNOWN") -> Page or None:
        return self.__operate_page__('GET', page_name, sender=sender)

    def save_new_page(self, page_name: str, content: str, summary: str = "BOT AUTO", sender="UNKNOWN") -> None:
        self.__operate_page__('CREATE', page_name, content=content, summary=summary, sender=sender)

    def delete_page(self, page_name: str, reason: str = "BOT AUTO", sender="UNKNOWN"):
        self.__operate_page__('DELETE', page_name, reason=reason, sender=sender)

    def __get_cur_operation_index__(self) -> int:
        self.__operation_index_mutex.acquire()
        ret = self.__operation_index
        self.__operation_index_mutex.release()
        return ret

    def __ask_for_operation_index__(self) -> int:
        self.__operation_index_mutex.acquire()
        ret = self.__operation_index
        self.__operation_index += 1
        self.__operation_index_mutex.release()
        return ret

    def __write_log__(self, message):
        with open(os.path.join('Logs', 'HuijiManager.log'), 'a') as fs:
            fs.write(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}][{'ONLINE' if self.__site_service.logged_in else 'OFFLINE'}]{message}{os.linesep}")
            fs.flush()

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

        def get_page():
            nonlocal tgt_page, page_name
            tgt_page = site_service.pages[page_name]

        def create_page():
            nonlocal tgt_page, page_name
            tgt_page = site_service.pages[page_name]
            if tgt_page.exists:
                return 'Duplicated page'
            else:
                tgt_page.save(content, summary=summary, bot=True)

        def delete_page():
            nonlocal tgt_page, page_name
            tgt_page = site_service.pages[page_name]
            if not tgt_page.exists:
                return 'Page does not exist'
            else:
                tgt_page.delete(reason=reason)

        page_operations_funcs = {
            'GET': get_page,
            'CREATE': create_page,
            'DELETE': delete_page
        }
        result = MediaWikiManager.__try_doing__(page_operations_funcs[operation_type],
                                                lambda e, c: self.__write_log__(
                                                    f"OPERATION[{operation_type}] to PAGE[{page_name}] from USER[{sender}] failed (OI[{my_operation_index}]), this is the {c}th failure(s)"
                                                    + os.linesep + e),
                                                retry_times, retry_interval)
        if result is None:
            self.__write_log__(
                f"OPERATION[{operation_type}] to PAGE[{page_name}] from USER[{sender}](OI[{my_operation_index}]) completed")
        else:
            self.__write_log__(
                f"OPERATION[{operation_type}] to PAGE[{page_name}] from USER[{sender}](OI[{my_operation_index}]) failed[{result}]")
        return tgt_page

    @staticmethod
    def __try_doing__(func, retry=None, retry_times: int = 10, retry_interval: int = 30) -> str or None:
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

    def __init__(self, account, password, host="gw2.huijiwiki.com"):
        self.__account = account
        self.__password = password
        self.__site_service = Site(host)
