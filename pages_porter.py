import json
import os
import re
from time import sleep
from mwclient import Site
import global_utils

_dict = global_utils.known_dict


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
    list_local_file = os.path.join(tgt_folder, f"{to_folder.split(os.pathsep)[-1]}.txt")
    if force_refresh_list or not os.path.exists(list_local_file):
        pages = global_utils.arena_manager.get_element_names_in_categories(categories)
        if not os.path.exists(tgt_folder):
            os.makedirs(tgt_folder)
        with open(list_local_file, 'w+', encoding='utf8') as F:
            F.write(json.dumps(pages, ensure_ascii=False))
    else:
        with open(list_local_file, 'r', encoding='utf8') as F:
            pages = json.load(F)
    return arena_download_all_pages(pages, tgt_folder)


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

# TODO 下列任务未完成
# def replFamily(matched):
#     text = matched.group(1)
#     text = text.replace('\r\n', "")
#     trans = {
#         'canine': '犬类',
#         'bear': '熊',
#         'armored fish': '装甲鱼',
#         'moa': '陆行鸟',
#         'spider': '蜘蛛',
#         'jellyfish': '水母',
#         'porcine': '猪类',
#         'bristleback': '钢背蜥',
#         'devourer': '噬蝎',
#         'feline': '灵猫',
#         'bird': '鸟类',
#         'wyvern': '翼龙',
#         'fanged iboga': '尖牙伊波茄',
#         'drake': '龙蜥',
#         'jacaranda': '蓝花楹',
#         'rock gazelle': '岩石羚羊',
#         'shark': '鲨鱼',
#         'smokescale': '雾鳞蜥',
#     }
#     res = trans[text.lower()]
#     res = 'family = ' + text + '\n| family_zh = ' + res + '\n'
#     return res
#
#
# def checkDict(string, _dict):
#     hasMatch = False
#     transRes = string
#
#     for cat in _dict:
#         if string in _dict[cat]:
#             hasMatch = True
#             transRes = _dict[cat][string]
#
#     return hasMatch, transRes
#
#
# def checkDict2(string, _dict):
#     hasMatch = False
#     transRes = string + ' —Acht'
#     print(transRes)
#
#     for cat in _dict:
#
#         if transRes in _dict[cat]:
#             hasMatch = True
#             transRes = _dict[cat][transRes]
#             print(transRes)
#
#     return hasMatch, transRes
#
#
# def replRegion(matched):
#     text = matched.group(1)
#     text = text.replace('\r', '')
#     text = text.split(',')
#     # print('region matched:', text)
#     res = 'region = '
#     for t in text:
#         _t = t
#         if _t[0] == ' ':
#             l = len(_t)
#             _t = _t[1:l]
#         hasMatch, trans = global_utils.look_up_known_dict(_t)
#         res = res + trans
#         if text.index(t) != len(text) - 1:
#             res = res + ','
#     # print('region transed:', res)
#
#     return res
#
#
# def replDesc(matched):
#     _text = matched.group(1)
#
#     _text = re.sub(r'\{\{.*\}\}', '', _text)
#
#     res = 'description = '
#     hasMatch, trans = checkDict2(_text, _dict)
#     res = res + trans
#     # print("::", trans)
#     return res
#
#
# def infobox(string, name):
#     # family
#     res = re.sub(r'family\s=\s([a-zA-Z\'\s]*)', replFamily, string)
#
#     # region
#     res = re.sub(r'region\s=\s(.*)', replRegion, res)
#
#     # remove interwiki
#     res = re.sub(r'\[\[[a-z]{2}\:.*\]\]', '', res)
#
#     res = re.sub(r'(region\s=\s.*)', r'\1\n| name = ' + str(name), res)
#     return res
#
#
# def headers(string):
#     res = string.replace('== Pet skills and attributes ==', '== 宠物技能与属性 ==')
#     res = res.replace('== Locations ==', '== 地点 ==')
#     return res
#
#
# def wikiLinks(string, _dict):
#     res = re.sub(r'\[\[([^\]]*)\]\]', transLink, string)
#     return res
#
#
# def transLink(matched):
#     s = matched.group(1)
#     res = s
#     """
#     寻找|左边的内容
#     """
#     match = re.search(r'(.*)\|(.*)', s)
#     if match is not None:
#         s = match.group(1)
#     """
#     翻译
#     """
#     hasMatch, tRes = global_utils.look_up_known_dict(name)
#
#     if hasMatch:
#         res = tRes
#
#     return '[[' + res + ']]'
#
#
# def processWikipage():
#     _list = []
#     getRawFile('H:\\gw2_2\\wikiText\\en\\pet\\', _list, 'WIKI')
#     # print(_list)
#     for p in _list:
#         name = p.split('\\')
#         name = name[-1].replace('.wiki', '')
#         hasMatch, name_zh = global_utils.look_up_known_dict(name)
#
#         name_zh = name_zh.replace('%2F', "/")
#         name_zh = name_zh.replace('%3A', ":")
#         name_zh = name_zh.replace('%2A', "*")
#         name_zh = name_zh.replace('%3F', "?")
#         name_zh = name_zh.replace('%22', '"')
#
#         with open(p, 'r', encoding='utf8', newline='') as W:
#             string = W.read()
#         # 处理 infobox
#         string = infobox(string, name)
#         # 处理链接
#         string = wikiLinks(string, _dict)
#         # 处理h2、h3、h4
#         string = headers(string)
#
#         string = '{{需要翻译}}' + string + '[[category:宠物]]'
#
#         site = Site('gw2.huijiwiki.com')
#         site.login('报警机器人', '  ')
#
#         _page = site.pages[name_zh]
#         _page.save(string, summary='搬运', bot=True)
#
#         print(name, name_zh)
#
#
# def getPetSkillPage():
#     site = Site('wiki.guildwars2.com', path='/')
#     page = site.pages['template:Skill infobox']  # 15509
#
#     e_pages = page.embeddedin(namespace=0)
#     count = 0
#     hit_count = 0
#     for e in e_pages:
#         name = e.name
#         _page = site.pages[name]
#         text = _page.text()
#         match = re.search(r'pet-family\s\=\s', text)
#         if match:
#
#             name = name.replace("/", '%2F')
#             name = name.replace(":", '%3A')
#             name = name.replace("*", '%2A')
#             name = name.replace("?", '%3F')
#             name = name.replace('"', '%22')
#
#             file = 'H:\\gw2_2\\wikiText\\en\\petSkill\\' + name + '.wiki'
#             if not os.path.exists(file):
#                 try:
#                     with open(file, 'w', encoding='utf8') as sF:
#                         sF.write(text)
#                     print(file + '.wiki')
#                 except Exception:
#                     sleep(30)
#                     pass
#             else:
#                 hasMatch, res = global_utils.look_up_known_dict(name)
#                 print("pass", file + '.wiki', res)
#
#
# def checkPetSkill():
#     h_site = Site('gw2.huijiwiki.com')
#     h_site.login('报警机器人', '  ')
#
#     page = h_site.pages['template:infobox skill']  # 15509
#
#     e_pages = page.embeddedin(namespace=0)
#
#     _list = []
#     getRawFile('H:\\gw2_2\\wikiText\\en\\petSkill\\', _list, 'WIKI')
#
#     for e in e_pages:
#         e_page = h_site.pages[e.name]
#         e_text = e_page.text()
#         match = re.search(r'pet-family\s\=\s', e_text)
#         if match:
#             _id = re.search(r'id\s\=\s([0-9]*)', e_text)
#             if _id:
#                 _id = _id.group(1)
#
#                 for i in _list:
#                     with open(i, 'r', encoding='utf8', newline='') as W:
#                         string = W.read()
#                     _i_id = re.search(r'id\s\=\s([0-9]*)', string)
#                     if _i_id:
#                         _i_id = _i_id.group(1)
#                         print(_i_id)
#                         if _id == _i_id:
#                             name = i.split('\\')
#                             name = name[-1].replace('.wiki', '')
#
#                             name = name.replace('%2F', "/")
#                             name = name.replace('%3A', ":")
#                             name = name.replace('%2A', "*")
#                             name = name.replace('%3F', "?")
#                             name = name.replace('%22', '"')
#
#                             e_text = re.sub(r'name\s\=\s.*', r'name = ' + name, e_text)
#                             # print(e_text)
#                             e_page.save(e_text, summary='更新', bot=True)
#                             print("update:", e.name)
#
#
# def getZH():
#     h_site = Site('gw2.huijiwiki.com')
#     h_site.login('报警机器人', '  ')
#     page = h_site.pages['template:infobox skill']  # 15509
#     e_pages = page.embeddedin(namespace=0)
#     pet = []
#     for e in e_pages:
#         e_page = h_site.pages[e.name]
#         name = e.name
#         e_text = e_page.text()
#         match = re.search(r'pet-family\s\=\s', e_text)
#         if match:
#             name = name.replace("/", '%2F')
#             name = name.replace(":", '%3A')
#             name = name.replace("*", '%2A')
#             name = name.replace("?", '%3F')
#             name = name.replace('"', '%22')
#
#             file = 'H:\\gw2_2\\wikiText\\zh\\petSkill\\' + name + '.wiki'
#             if not os.path.exists(file):
#                 try:
#                     with open(file, 'w', encoding='utf8') as sF:
#                         sF.write(e_text)
#                     print(file + '.wiki')
#                 except Exception:
#                     sleep(30)
#                     pass
#
#
# def getZH2():
#     _list = []
#     getRawFile('H:\\gw2_2\\wikiText\\zh\\skill\\', _list, 'WIKI')
#
#     for e in _list:
#         with open(e, 'r', encoding='utf8', newline='') as W:
#             string = W.read()
#
#         match = re.search(r'pet-family\s\=\s', string)
#         if match:
#             name = e.split('\\')
#             name = name[-1].replace('.wiki', '')
#
#             file = 'H:\\gw2_2\\wikiText\\zh\\petSkillOld\\' + name + '.wiki'
#             if not os.path.exists(file):
#                 try:
#                     with open(file, 'w', encoding='utf8') as sF:
#                         sF.write(string)
#                     print(file + '.wiki')
#                 except Exception:
#                     sleep(30)
#                     pass
#
#
# def checkPetSkill2():
#     # 登陆网站
#     h_site = Site('gw2.huijiwiki.com')
#     h_site.login('报警机器人', '  ')
#
#     zh_list = []
#     # 从网站上down下来的所有petSkill页面
#     getRawFile('H:\\gw2_2\\wikiText\\zh\\petSkill\\', zh_list, 'WIKI')
#
#     en_list = []
#     getRawFile('H:\\gw2_2\\wikiText\\en\\petSkill\\', en_list, 'WIKI')
#
#     for zh_page in zh_list:
#         with open(zh_page, 'r', encoding='utf8', newline='') as Z:
#             zh_Text = Z.read()
#         _zh_id = re.search(r'id\s\=\s([0-9]*)', zh_Text)
#         if _zh_id:
#             _zh_id = _zh_id.group(1)
#         _zh_name = re.search(r'name\s\=\s([\w\s\']*)', zh_Text)
#         if _zh_name:
#             _zh_name = _zh_name.group(1)
#
#         fileName = zh_page.split('\\')
#         fileName = fileName[-1].replace('.wiki', '')
#
#         name_bracket = re.search(r'(\s\([\w\s\']*\))', fileName)
#         if name_bracket:
#             name_bracket = name_bracket.group(1)
#             # print('>>>>>>', name_bracket.group(1))
#
#         if not _zh_name:
#             if _zh_id:
#                 for en_page in en_list:
#                     with open(en_page, 'r', encoding='utf8', newline='') as E:
#                         en_Text = E.read()
#                     _en_id = re.search(r'id\s\=\s([0-9]*)', en_Text)
#                     # 有 id
#                     if _en_id:
#                         _en_id = _en_id.group(1)
#
#                         if _zh_id == _en_id:
#                             en_name = en_page.split('\\')
#                             en_name = en_name[-1].replace('.wiki', '')
#                             en_name = en_name.replace('%2F', "/")
#                             en_name = en_name.replace('%3A', ":")
#                             en_name = en_name.replace('%2A', "*")
#                             en_name = en_name.replace('%3F', "?")
#                             en_name = en_name.replace('%22', '"')
#
#                             zh_Text = re.sub(r'\{\{infobox skill', '{{infobox skill\n| name = ' + en_name, zh_Text)
#
#                             # print(_zh_name, zh_Text)
#             else:
#                 print(_zh_name, zh_Text)
#
#
# def delete():
#     h_site = Site('gw2.huijiwiki.com')
#     h_site.login('报警机器人', '  ')
#     page = h_site.pages['template:infobox skill']  # 15509
#     e_pages = page.embeddedin(namespace=0)
#
#     for e in e_pages:
#         p = h_site.pages[e.name]
#         p.delete(reason='维护')
#
#
# def checkTraitPage():
#     data_list = []
#     getRawFile('H:\\gw2_2\\data\\v2_traits\\', data_list, 'JSON')
#
#     en_list = []
#     getRawFile('H:\\gw2_2\\wikiText\\en\\traits\\', en_list, 'WIKI')
#
#     for d in data_list:
#         with open(d, 'r', encoding='utf8', newline='') as D:
#             data_dict = json.load(D)
#         _id = data_dict['id']
#         hasMatch = False
#         for e in en_list:
#             with open(e, 'r', encoding='utf8', newline='') as E:
#                 en_Text = E.read()
#             _en_id = re.search(r'id\s\=\s([0-9]*)', en_Text)
#             if _en_id:
#                 _en_id = _en_id.group(1).replace(' ', '')
#                 _en_id = _en_id.replace('\n', '')
#                 _en_id = _en_id.replace('\r', '')
#                 _en_id = _en_id.replace('\t', '')
#                 # print(">>>", _id, _en_id)
#             if str(_id) == str(_en_id):
#                 hasMatch = True
#         if not hasMatch:
#             print('missing:', _id, data_dict['name'])
# else:
# print('found:', _id, data_dict['name'])


# checkTraitPage()
# getenwikiPage()
# processWikipage()
# checkPetSkill()
# getZH2()
# checkPetSkill2()
# getPetSkillPage()
# delete()
# getenwikiPageMount()
# getenwikiPageMountLisence()
# getenwikiPageItem()
# getenwikiPageItemList()
