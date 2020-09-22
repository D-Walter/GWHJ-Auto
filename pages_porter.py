import os
from mwclient.page import Page
import global_utils
from media_wiki_manager import MediaWikiManager
import re


def arena_get_pet_skills_pages(to_folder: str):
    list_page = global_utils.arena_manager.get_page('template:Skill infobox')
    for e in list_page.embeddedin(namespace=0):
        page_pointer = global_utils.arena_manager.get_page(e.name)
        text = page_pointer.text()
        match = re.search(r'pet-family\s=\s', text)
        if match:
            MediaWikiManager.download_single_page(e, global_utils.get_path([to_folder]))


def arena_get_page_mounts(force_refresh=False) -> (int, list):
    return global_utils.arena_manager.download_all_pages_in_categories(['Griffon skins',
                                                                        'Jackal skin',
                                                                        'Jackal skins',
                                                                        'Raptor skins',
                                                                        'Roller Beetle skins',
                                                                        'Skimmer skins',
                                                                        'Skyscale skins',
                                                                        'Springer skins',
                                                                        'Warclaw skins',
                                                                        'Gem Store mounts'], global_utils.get_path(
        ["wikiText", "en", "mounts"]),
                                                                       force_refresh)


def arena_get_mount_licenses(force_refresh=False) -> (int, list):
    return global_utils.arena_manager.download_all_pages_in_categories(['Gem Store mount licenses'],
                                                                       global_utils.get_path(
                                                                           ["wikiText", "en", "mount licenses"]),
                                                                       force_refresh)


def arena_get_items(force_refresh=False) -> (int, list):
    return global_utils.arena_manager.download_all_pages_in_categories(["items"],
                                                                       global_utils.get_path(
                                                                           ["wikiText", "en", "items"]),
                                                                       force_refresh)


def arena_get_pages_embedded_with(embedded_page_name: str, to_folder: str):
    pages = global_utils.arena_manager.get_page(embedded_page_name).embeddedin(namespace=0)  # 15509
    global_utils.arena_manager.download_all_pages(pages, global_utils.get_path([to_folder]))

