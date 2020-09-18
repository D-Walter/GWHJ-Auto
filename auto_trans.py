import csv
import json
import os
import re
from time import sleep

import global_utils

TRANS = {}
_count = 0
_match = 0


def transLink2(matched):
    s = matched.group(1)
    res = s
    _dict = {
        'Guardian': '守护者',
        'Revenant': '魂武者',
        'Warrior': '战士',
        'Engineer': '工程师',
        'Ranger': '游侠',
        'Thief': '潜行者',
        'Elementalist': '元素使',
        'Mesmer': '幻术师',
        'Necromancer': '唤灵师',
        'Zeal': '热诚',
        'Radiance': '光辉',
        'Valor': '英勇',
        'Honor': '荣耀',
        'Virtues': '美德',
        'Dragonhunter': '猎龙者',
        'Firebrand': '燃火者',
        'Corruption': '力量',
        'Retribution': '武器',
        'Salvation': '防御',
        'Devastation': '战术',
        'Invocation': '纪律',
        'Herald': '龙魂使',
        'Renegade': '预告者',
        'Strength': '力量',
        'Arms': '武器',
        'Defense': '防御',
        'Tactics': '战术',
        'Discipline': '纪律',
        'Berserker': '狂战士',
        'Spellbreaker': '破法者',
        'Explosives': '炸药',
        'Firearms': '枪械',
        'Inventions': '发明',
        'Alchemy': '炼金',
        'Tools': '工具',
        'Scrapper': '机械师',
        'Holosmith': '全息师',
        'Marksmanship': '射手',
        'Skirmishing': '游击',
        'Wilderness Survival': '生存',
        'Nature Magic': '自然',
        'Beastmastery': '兽王',
        'Druid': '德鲁伊',
        'Soulbeast': '魂兽师',
        'Deadly Arts': '武艺',
        'Critical Strikes': '致命',
        'Shadow Arts': '暗影',
        'Acrobatics': '技巧',
        'Trickery': '诡诈',
        'Daredevil': '独行侠',
        'Deadeye': '神枪手',
        'Fire': "火焰",
        'Air': "空气",
        'Earth': "大地",
        'Water': "流水",
        'Arcane': "秘法",
        'Tempest': "暴风使",
        'Weaver': "编织者",
        'Domination': '支配',
        'Dueling': '决斗',
        'Chaos': '混沌',
        'Inspiration': '灵感',
        'Illusions': '幻象',
        'Chronomancer': '时空术士',
        'Mirage': '幻象术士',
        'Spite': '怨恨',
        'Curses': '诅咒',
        'Death Magic': '死亡',
        'Blood Magic': '鲜血',
        'Soul Reaping': '摄魂',
        'Reaper': '夺魂者',
        'Scourge': '灾厄师',
    }
    """
    寻找|左边的内容
    """
    match = re.search(r'(.*)\|(.*)', s)
    if match is not None:
        s = match.group(1)
    """
    翻译
    """
    if res in _dict:
        res = _dict[res]

    return '[[' + res + ']]'


def headerLink(matched):
    res = matched.group(2)
    enums = {
        'Mounts': "坐骑",
        'Screenshots': "截图",
        'Event': "事件",
        'Weapons': "武器",
        'Historical abilities': "史实技能",
        'Large variant': "大型变体",
        'Related achievements': "相关成就",
        'Personal story': "个人故事",
        'Upgrades': "升级",
        'Historical Dialogue': "史实对话",
        'Common Weapon Skins': "普通武器皮肤",
        'Trivia': "轶事",
        'Appearances': "外表",
        'Miscellaneous': "杂项",
        'PvP items': "PVP物品",
        'Material': "材料",
        'Historical content': "史实内容",
        'Related events': "相关事件",
        'Locations': "地点",
        'Historical location': "史实地点",
        'Notes': "注意",
        'Combat abilities': "战斗技能",
        'Items offered': "提供物品",
        'Dialogue': "对话",
        'Event involvement': "事件相关",
        'Quotes': "引言",
        'Gallery': "画廊",
        'Location': "地点",
        'Related[[trait]]s': "相关[[特性]]",
        'Versionhistory': "版本历史",

    }
    s = matched.group(2)
    s = s.replace(' ', '')

    if s in enums:
        res = enums[s]

    return matched.group(1) + ' ' + res + ' ' + matched.group(3)


def headerLink2(matched):
    return matched.group(1)


def dialogueTrans(matched):
    s = matched.group(1)
    res = s
    for c in global_utils.known_dict:
        if s in global_utils.known_dict[c]:
            res = global_utils.known_dict[c][s]
    return "''" + res + "''"


def dialogueTrans2(matched):
    s = matched.group(2)
    res = s
    for c in global_utils.known_dict:
        if s in global_utils.known_dict[c]:
            res = global_utils.known_dict[c][s]
    return matched.group(1) + res + '\n'


repl_dict = {
    "links": [r'\[\[([^]]*)]]', transLink2],
    "headers": [r'(={2,4})\s*([\S]?)\s*(={2,4})', headerLink],
    "dialogues1": [r'(<small>.*</small>)', ''],
    "dialogues2": [r'\'\'(.*)\'\'', dialogueTrans],
    "dialogues3": [r'(:{1,4})(.*)\n', dialogueTrans2],
    "去空格": [r" ==", "=="],
}


# 将一个英文wiki界面标准化至灰机wiki标准
def standardize_page(content: str, name: str) -> str:
    for p_string, rep_func in repl_dict:
        content = re.sub(p_string, rep_func, content)
    return content


def normal_save(content, name):
    global_utils.huiji_manager.save_new_page(global_utils.get_standardized_name(name), content)


# 一般页面处理流程，包括了页面标准化和上传处理
def normal_pages_process(root: str, basic_handle=standardize_page, upload_handle=normal_save) -> None:
    for temp_content, page_name in global_utils.get_wiki_files(root):
        temp_content, page_name = basic_handle(temp_content, page_name)
        upload_handle(temp_content, page_name)


# 处理技能导航navbox相关
def process_page_skill_navs(mode):
    def handle(content, name):
        nonlocal mode
        if mode == 'c':
            match = re.search(r'id\s+=([\s0-9,]*)', content)
            if match is not None:
                ids = match.group(1).replace(' ', '')
                ids = ids.replace('\n', '')
                ids = ids.split(',')
                print("id", match.group(1))
                for _id in ids:
                    r_name = 'Skills/' + str(_id)
                    r_name = re.sub(r'\s', '', r_name)
                    print('r_name', r_name)
                    global_utils.huiji_manager.save_new_page(r_name, '#重定向 [[' + name + ']]', summary='bot')
            global_utils.huiji_manager.save_new_page(f'技能/{name}', content)
            global_utils.huiji_manager.delete_page(name)
        else:
            print(content)
    normal_pages_process(global_utils.get_path(['wikiText', 'zh', 'skill']), upload_handle=handle)


def replace_family(matched):
    text = matched.group(1)
    text = text.replace('\r\n', "")
    trans = {
        'canine': '犬类',
        'bear': '熊',
        'armored fish': '装甲鱼',
        'moa': '陆行鸟',
        'spider': '蜘蛛',
        'jellyfish': '水母',
        'porcine': '猪类',
        'bristleback': '钢背蜥',
        'devourer': '噬蝎',
        'feline': '灵猫',
        'bird': '鸟类',
        'wyvern': '翼龙',
        'fanged iboga': '尖牙伊波茄',
        'drake': '龙蜥',
        'jacaranda': '蓝花楹',
        'rock gazelle': '岩石羚羊',
        'shark': '鲨鱼',
        'smokescale': '雾鳞蜥',
    }
    res = 'family = ' + text + '\n| family_zh = ' + trans[text.lower()] + '\n'
    return res


def replace_region(matched):
    text = matched.group(1)
    text = text.replace('\r', '')
    text = text.split(',')
    # print('region matched:', text)
    res = ""
    for t in text:
        _t = t
        if _t[0] == ' ':
            l = len(_t)
            _t = _t[1:l]
        has_matched, trans = global_utils.look_up_known_dict(_t)
        res = f"region = {trans}"
        if text.index(t) != len(text) - 1:
            res = f"{res},"
    # print('region transed:', res)
    return res


def replace_description(matched):
    _text = matched.group(1)
    _text = re.sub(r'{{.*}}', '', _text)
    res = 'description = '
    has_matched, trans = global_utils.look_up_known_dict(_text)
    res = res + trans
    # print("::", trans)
    return res


def infobox(string, name):
    # family
    res = re.sub(r'family\s=\s([a-zA-Z\'\s]*)', replace_family, string)
    # region
    res = re.sub(r'region\s=\s(.*)', replace_region, res)
    # remove interwiki
    res = re.sub(r'\[\[[a-z]{2}:.*]]', '', res)
    res = re.sub(r'(region\s=\s.*)', r'\1\n| name = ' + str(name), res)
    return res


def replace_headers(string):
    headers_dic = {
        ['== Pet skills and attributes ==', '== 宠物技能与属性 =='],
        ['== Locations ==', '== 地点 ==']
    }
    res = string
    for header in headers_dic:
        res = res.replace(header[0], header[1])
    return res


def translate_inner_links(string, _dict):
    def _translate_inner_link(matched) -> str:
        _s = matched.group(1)
        match = re.search(r'(.*)\|(.*)', _s)
        _hasMatch, _res = global_utils.look_up_known_dict(match.group(1) if match is not None else _s)
        return '[[' + _res + ']]' if _hasMatch else _s
    res = re.sub(r'\[\[([^]]*)]]', _translate_inner_link, string)
    return res


def update_pets_skills():
    for e in global_utils.huiji_manager.get_page('template:infobox skill').embeddedin(namespace=0): # 15509
        e_page = global_utils.huiji_manager.get_page(e.name)
        e_text = e_page.text()
        if re.search(r'pet-family\s=\s', e_text):
            _id = re.search(r'id\s=\s([0-9]*)', e_text)
            if _id:
                _id = _id.group(1)
                for l_file in global_utils.get_wiki_files(global_utils.get_path(["wikiText","en","petSkill"])):
                    with open(l_file, 'r', encoding='utf8', newline='') as W:
                        string = W.read()
                    _i_id = re.search(r'id\s=\s([0-9]*)', string)
                    if _i_id:
                        if _id == _i_id.group(1):
                            name = global_utils.get_standardized_name(l_file)
                            e_text = re.sub(r'name\s=\s.*', r'name = ' + name, e_text)
                            e_page.save(e_text, summary='更新', bot=True)
                            print("update:", e.name)

def update_pets_skills_local():
    for zh_file in global_utils.get_wiki_files(global_utils.get_path(["wikiText","zh","petSkill"])):
        with open(zh_file, 'r', encoding='utf8', newline='') as fs:
            zh_content = fs.read()
        zh_id = re.search(r'id\s=\s([0-9]*)', zh_content)
        if zh_id:
            _zh_id = zh_id.group(1)
        zh_name = re.search(r'name\s=\s([\w\s\']*)', zh_content)
        if zh_name:
            zh_name = zh_name.group(1)
        if not zh_name:
            if zh_id:
                for en_file in global_utils.get_wiki_files(global_utils.get_path(["wikiText","en","petSkill"])):
                    with open(en_file, 'r', encoding='utf8', newline='') as fs:
                        en_content = fs.read()
                    en_id = re.search(r'id\s=\s([0-9]*)', en_content)
                    if en_id:
                        en_id = en_id.group(1)
                        if zh_id == en_id:
                            en_name = global_utils.get_standardized_name(en_file)
                            zh_content = re.sub(r'{{infobox skill', '{{infobox skill\n| name = ' + en_name, zh_content)


def get_pets_skills_from_huiji():
    for e in global_utils.huiji_manager.get_page('template:infobox skill').embeddedin(namespace=0):
        e_page = global_utils.huiji_manager.get_page(e.name)
        e_content = e_page.text()
        if re.search(r'pet-family\s=\s', e_content):
            file = global_utils.get_path(['wikiText','zh','petSkill',f'{global_utils.get_ascii_name(e.name)}.wiki'])
            if not os.path.exists(file):
                with open(file, 'w', encoding='utf8') as fs:
                    fs.write(e_content)
                print(file + '.wiki')
# TODO 下列任务未完成


def checkTraitPage():
    data_list = []
    getRawFile('H:\\gw2_2\\data\\v2_traits\\', data_list, 'JSON')

    en_list = []
    getRawFile('H:\\gw2_2\\wikiText\\en\\traits\\', en_list, 'WIKI')

    for d in data_list:
        with open(d, 'r', encoding='utf8', newline='') as D:
            data_dict = json.load(D)
        _id = data_dict['id']
        hasMatch = False
        for e in en_list:
            with open(e, 'r', encoding='utf8', newline='') as E:
                en_Text = E.read()
            _en_id = re.search(r'id\s\=\s([0-9]*)', en_Text)
            if _en_id:
                _en_id = _en_id.group(1).replace(' ', '')
                _en_id = _en_id.replace('\n', '')
                _en_id = _en_id.replace('\r', '')
                _en_id = _en_id.replace('\t', '')
                # print(">>>", _id, _en_id)
            if str(_id) == str(_en_id):
                hasMatch = True
        if not hasMatch:
            print('missing:', _id, data_dict['name'])
        else:
        print('found:', _id, data_dict['name'])



# 处理item（物品，包括一部分皮肤）
def preprocessPageItems():
    p_list = []
    sub_cat_list = []
    getRawFile('H:\\gw2_2\\wikiText\\en\\items', p_list, 'WIKI')

    for w in p_list:
        with open(w, 'r', encoding='utf8', newline='') as W:
            string = W.read()
        subcategory = ''
        subcategory_m = re.search('{{([\w]+) infobox', string)
        if subcategory_m:
            subcategory = subcategory_m.group(1)

        if subcategory not in sub_cat_list:
            sub_cat_list.append(subcategory)

    with open('H:\\gw2_2\\preprocessItems.json', 'w', encoding='utf8') as F:
        F.write(json.dumps(sub_cat_list, ensure_ascii=False))


# 通用，在arena的wiki页面中寻找【有效】id
def arena_find_id(arena_content):
    p = 0
    match = re.search(r'(\n}})', arena_content, re.X)
    if match is not None:
        p = match.span(1)
        p = p[0]
    match = re.search(r'\| id\s+=([\s0-9,]*)', arena_content)
    if match is not None:
        p2 = match.span(1)
        p2 = p2[0]
        if p > p2:
            return True, match.group(1)
        else:
            return False, 'fffff'
    else:
        return False, 'fffff'


# 处理arena页面中物品相关
def process_items_content(_string, w, data_dict, _id, hasID=True):
    string = wikiLinks3(_string)
    # 处理h2、h3、h4
    _repl_dict = [
        [r'==[\s]*Acquisition[\s]*==', '== 获取方法 =='],
        [r'==[\s]*Contents[\s]*==', '== 包含物品 =='],
        [r'===[\s]*Contained in[\s]*===', '== 包含于 =='],
        [r'===[\s]*Gathered from[\s]*===', '== 收集自 =='],
        [r'===[\s]*Dropped by[\s]*===', '== 掉落自 =='],
        [r'===[\s]*\[\[Map Bonus Reward]][\s]*===', '== [[地图奖励]] =='],
        [r'==[\s]*Used in[\s]*==', '== 用途 =='],
        [r'==[\s]*Currency for[\s]*==', '== 货币兑换 =='],
        [r'==[\s]*Trivia[\s]*==', '== 趣闻 =='],
        [r'==[\s]*Weapon variants[\s]*==', '== 相关武器 =='],
        [r'==[\s]*Available prefixes[\s]*==', '== 属性前缀 =='],
        [r'==[\s]*Salvage results[\s]*==', '== 拆解 =='],
        [r'==[\s]*Notes[\s]*==', '== 说明 =='],
        [r'==[\s]*Salvages into[\s]*==', '== 拆解 =='],
        [r'==[\s]*See also[\s]*==', '== 另见 =='],
        [r'==[\s]*Variants[\s]*==', '== 衍生 =='],
    ]
    for r in repl_dict:
        string = re.sub(r[0], r[1], string)

    # 处理 infobox
    string, name, name_s, hasBracket, bracket = infoboxItems(string, w, data_dict, _id, hasID)

    string = '{{需要翻译}}\n' + string
    return string, name, name_s, hasBracket, bracket


# 处理Arena页面infobox中没有id，但是页面中有N个关联id的情况（常见于一个物品模板和他的N个衍生变种，arena是合并在一个页面里的）
def itemsProcessReturnID(__string, __w):
    _ids = []
    match1 = re.search('{{fm table', __string)
    if match1 is not None:
        fid = re.search(r'\| fid = (\d+)', __string)
        mid = re.search(r'\| mid = (\d+)', __string)

        if fid is not None:
            _ids.append(fid.group(1))
        if mid is not None:
            _ids.append(mid.group(1))

    match2 = re.search('{{Dungeon equipment', __string)
    if match2 is not None:
        sub_id = re.findall(r'\| id[\d]+ = ([\d]+)', __string)
        if sub_id is not None:
            print(sub_id)
            for _sub_id in sub_id:
                _ids.append(_sub_id)

    match3 = re.search(r'variant table header', __string)
    if match3 is not None:
        variant_id = re.findall(r'\| id = ([\d]+)', __string)
        if variant_id is not None:
            for _v_id in variant_id:
                _ids.append(_v_id)
    return _ids


# 处理arena物品页面的通用模块
def processPageItems(mode):
    p_list = []
    getRawFile('H:\\gw2_2\\wikiText\\en\\items', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    set = {}
    override = ''
    __count1 = 0
    __count2 = 0
    __count3 = 0
    for l_file in global_utils.get_wiki_files(global_utils.get_path(["wikiText","en","items"])):
        with open(l_file, 'r', encoding='utf8', newline='') as fs:
            content = fs.read()
        # 移除注释
        content = re.sub(r'<!--(.*)-->', '', content)

        # get subcategory
        subcategory = re.search(r'{{([\w\s]+) infobox', content)
        if subcategory:
            subcategory = subcategory.group(1)

        # id
        id_match, matched_id = arena_find_id(content)
        # isHistorical
        is_historical = re.search(r'\| status = historical', content) is not None

        _items = [
            "item",
            "weapon",
            "dye",
            "inventory",
            "armor",
            "trinket",
            "upgrade component",
            "back item"
        ]
        _excluded = [
            'dye',
            'skin'
        ]
        if subcategory.lower() in _items:
            data_dict = {}
            # 不是历史物品
            if not is_historical:
                # 有id
                if id_match:
                    _ids = matched_id.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
                    # 可能有多个id
                    _ids = _ids.split(',')
                    for _id in _ids:
                        if _id != '':
                            js_file = global_utils.get_path(["data","v2_items",f"v2_items_{str(_id)}.json"])
                            if os.path.exists(js_file):
                                with open(js_file, 'r', encoding='utf8', newline='') as fs:
                                    data_dict = json.load(fs)

                            string = content
                            # 处理链接
                            string, name, name_s, hasBracket, bracket = process_items_content(string, l_file, data_dict, _id)

                            if 'name_zh' in data_dict:
                                pageName = data_dict['name_zh']
                            else:
                                hasMatch, pageName = checkTranslation(name_s, _dict)

                            fullPageName = pageName
                            # 有括号
                            if hasBracket:
                                match = re.search(r'id\s+=([\s0-9,]*)', string)
                                # 有id
                                if match:
                                    fullPageName = fullPageName + '(' + bracket + ')'

                            # mountPage = site.pages[fullPageName]
                            if mode == 'c':
                                pass
                                # mountPage.save(string, summary='新坐骑领养证页面', bot=True)
                            elif mode == 'l':
                                new_name = l_file.split('\\')
                                new_name = new_name[-1]

                                path = 'H:\\gw2_2\\wikiText\\zh\\items\\'

                                # 名字里是否包含 #
                                match = re.search('#', new_name)
                                # 有# 是子页面（无需保存文件）
                                if match is not None:
                                    if os.path.exists('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name):
                                        os.remove('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name)
                                else:
                                    # override
                                    if str(_id) in set:
                                        override = override + new_name + ' | ' + str(_id) + 'ovveride>>>>>>>' + set[
                                            str(_id)] + '\n'
                                    else:
                                        set[str(_id)] = new_name

                                        with open(path + str(_id) + '.wiki', 'w', encoding='utf8', newline='') as D:
                                            D.write(string)

                                        # delete
                                        if os.path.exists('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name):
                                            os.remove('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name)
                                        # print("item page:", fullPageName, _id, string)
                                        __count1 += 1
                                        # print("========================================================")
                # 没有id
                else:
                    # print(w)
                    new_name = l_file.split('\\')
                    new_name = new_name[-1]
                    # 名字里是否包含 #
                    match = re.search('#', new_name)
                    # 有# 是子页面（无需保存文件）
                    if match is not None:
                        if os.path.exists('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name):
                            os.remove('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name)
                    # 没有# 不是子页面
                    else:
                        __ids = itemsProcessReturnID(content, l_file)
                        # 至少包含1个有效的id
                        if len(__ids) > 0:
                            for __id in __ids:
                                string = content
                                string, name, name_s, hasBracket, bracket = process_items_content(string, l_file, data_dict,
                                                                                                  __id, False)

                                # 删除
                                if os.path.exists('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name):
                                    os.remove('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name)

                                # 寻找可能存在的覆盖项目
                                if str(__id) in set:
                                    override = override + new_name + ' | ' + str(__id) + 'ovveride>>>>>>>' + set[
                                        str(__id)] + '\n'

                                else:
                                    set[str(__id)] = new_name

                                    with open('H:\\gw2_2\\wikiText\\zh\\items\\' + str(__id) + '.wiki', 'w',
                                              encoding='utf8', newline='') as nD:
                                        nD.write(string)
                                    __count1 += 1
                                    print(">>>:", __id, name, string)
                        # 一个id都没有
                        else:
                            __count2 += 1
                            string, name, name_s, hasBracket, bracket = process_items_content(content, l_file, data_dict, '',
                                                                                              False)
                            with open('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name, 'w', encoding='utf8',
                                      newline='') as nnD:
                                nnD.write(string)
                            print("]]]:", new_name, string)
            else:
                __count3 += 1
                new_name = l_file.split('\\')
                new_name = new_name[-1]
                string, name, name_s, hasBracket, bracket = process_items_content(content, l_file, data_dict, '', False)
                with open('H:\\gw2_2\\wikiText\\zh\\items historical\\' + new_name, 'w', encoding='utf8',
                          newline='') as hD:
                    hD.write(string)

    print("count with id:", __count1)
    print("count without id:", __count2)
    print("count historical:", __count3)
    print("============override===========")
    print(override)


# 将处理好的文件保存在本地，以便更新到中文wiki
def updatePageItems(mode):
    d_list = []

    # load log
    if os.path.exists('H:\\gw2_2\\wiki_page_update_log_item.json'):
        with open('H:\\gw2_2\\wiki_page_update_log_item.json', 'r', encoding='utf8') as logF:
            log = json.load(logF)
    else:
        log = []

    getRawFile('H:\\gw2_2\\data\\v2_items', d_list, 'JSON')
    site = Site('gw2.huijiwiki.com', scheme='http')
    site.login('报警机器人', ' ')
    for d in d_list:
        with open(d, 'r', encoding='utf8', newline='') as D:
            data = json.load(D)
        _id = data['id']

        # page name
        page_name = 'items/' + str(_id)

        # bypass pages already updated
        if page_name not in log:
            wiki_page = site.pages[page_name]

            # wikitext
            zh_page = 'H:\\gw2_2\\wikiText\\zh\\items\\' + str(_id) + '.wiki'

            if os.path.exists(zh_page):
                with open(zh_page, 'r', encoding='utf8', newline='') as W:
                    zh_string = W.read()
                if mode == 'c':
                    # save log
                    with open('H:\\gw2_2\\wiki_page_update_log_item.json', 'w+', encoding='utf8') as logF:
                        logF.write(json.dumps(log, ensure_ascii=False))
                    try:
                        print("[1]:", d, page_name, zh_string)
                        wiki_page.save(zh_string, summary="更新物品页面(1)", bot=True)
                        log.append(page_name)
                    except PermissionError:
                        sleep(30)
                        pass
                else:
                    print("[1]:", page_name)
            else:
                # 不存在arena的页面
                zh_string = '{{infobox item\n'
                zh_string = zh_string + '| id = ' + str(_id) + '\n'
                zh_string = zh_string + '}}\n\n'
                zh_string = zh_string + '== 配方 ==\n'
                zh_string = zh_string + '{{Recipe}}\n\n'
                zh_string = zh_string + '{{ItemsModules|' + str(_id) + '}}\n'
                zh_string = zh_string + '{{Navbox/Item|' + str(_id) + '}}\n'
                if mode == 'c':
                    # save log
                    with open('H:\\gw2_2\\wiki_page_update_log_item.json', 'w+', encoding='utf8') as logF:
                        logF.write(json.dumps(log, ensure_ascii=False))

                    try:
                        print("[2]:", page_name)
                        wiki_page.save(zh_string, summary="更新物品页面(2)", bot=True)
                        log.append(page_name)
                    except PermissionError:
                        sleep(30)
                        pass

                else:
                    print("[2]:", page_name)

    p_list = []
    getRawFile('H:\\gw2_2\\wikiText\\zh\\items\\', p_list, 'WIKI')
    for p in p_list:
        with open(p, 'r', encoding='utf8', newline='') as W:
            zh_string = W.read()
        name = p.split('\\')
        name = name[-1].replace('.wiki', '')
        _id = name
        page_name = 'items/' + str(_id)

        # bypass pages already updated
        if page_name not in log:
            wiki_page = site.pages[page_name]
            if not wiki_page.exists:
                if mode == 'c':
                    # save log
                    with open('H:\\gw2_2\\wiki_page_update_log_item.json', 'w+', encoding='utf8') as logF:
                        logF.write(json.dumps(log, ensure_ascii=False))
                    try:
                        print("[3]:", page_name)
                        wiki_page.save(zh_string, summary="更新物品页面(3)", bot=True)
                        log.append(page_name)
                    except PermissionError:
                        sleep(30)
                        pass

                else:
                    print("[3]:", page_name)


# 处理arena页面-坐骑通行证相关
def processPageMountLisence(mode):
    pageNameSet = []
    r_log = ''
    p_log = ''
    error = ''
    p_list = []
    string = ''
    header_s = set()
    getRawFile('H:\\gw2_2\\wikiText\\en\\mount licenses', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    for w in p_list:
        with open(w, 'r', encoding='utf8', newline='') as W:
            string = W.read()

        # 有id
        match = re.search(r'id\s+=([\s0-9,]*)', string)

        data_dict = {}
        if match:
            _id = match.group(1).replace(' ', '')
            _id = _id.replace('\n', '')
            _id = _id.replace('\r', '')
            _ids = _id.split(',')
            _id = _ids[0]
            file = 'H:\\gw2_2\\data\\v2_items\\v2_items_' + str(_id) + '.json'
            if os.path.exists(file):
                with open(file, 'r', encoding='utf8', newline='') as D:
                    data_dict = json.load(D)

        # 处理链接
        string = wikiLinks3(string, _dict)
        # 处理h2、h3、h4
        string = re.sub(r'\=\=[\s]*Acquisition[\s]*\=\=', '== 获取方法 ==', string)
        string = re.sub(r'\=\=[\s]*Contents[\s]*\=\=', '== 内容 ==', string)
        string = re.sub(r'\=\=[\s]*Notes[\s]*\=\=', '== 注意 ==', string)
        string = re.sub(r'\=\=[\s]*Gallery[\s]*\=\=', '== 画廊 ==', string)
        string = re.sub(r'\=\=[\s]*Sold by[\s]*\=\=', '== 售卖于 ==', string)
        string = re.sub(r'\=\=[\s]*Contained in[\s]*\=\=', '== 包括于 ==', string)
        string = re.sub(r'\=\=[\s]*Raptor skins[\s]*\=\=', '== 肉食鸟皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Springer skins[\s]*\=\=', '== 弹跳兔皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Skimmer skins[\s]*\=\=', '== 飞鱼皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Jackal skins[\s]*\=\=', '== 胡狼皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Griffon skins[\s]*\=\=', '== 狮鹫皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Roller Beetle skins[\s]*\=\=', '== 翻滚甲虫皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Warclaw skins[\s]*\=\=', '== 战爪皮肤 ==', string)
        string = re.sub(r'\=\=[\s]*Skyscale skins[\s]*\=\=', '== 飞天鳞龙皮肤 ==', string)
        string = string.replace('[[Category:Gem Store mount licenses]]', '[[category:宝石商店坐骑许可证]]')

        # 处理 infobox
        string, name, name_s, hasBracket, bracket = infoboxMountLcenses(string, w, data_dict)

        string = '{{需要翻译}}\n' + string + '[[category:搬运页面]][[category:坐骑领养证]]\n'

        if 'name_zh' in data_dict:
            pageName = data_dict['name_zh']
        else:
            hasMatch, pageName = checkTranslation(name_s, _dict)

        fullPageName = pageName
        # 有括号
        if hasBracket:
            match = re.search(r'id\s+=([\s0-9,]*)', string)
            # 有id
            if match:
                fullPageName = fullPageName + '(' + bracket + ')'

        mountPage = site.pages[fullPageName]
        if mode == 'c':
            mountPage.save(string, summary='新坐骑领养证页面', bot=True)

        print("mount page:", fullPageName, string)
        print("========================================================")


# 处理arena页面-坐骑相关
def processPageMount(mode):
    pageNameSet = []
    r_log = ''
    p_log = ''
    error = ''
    p_list = []
    string = ''
    header_s = set()
    getRawFile('H:\\gw2_2\\wikiText\\en\\mounts', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    for w in p_list:
        with open(w, 'r', encoding='utf8', newline='') as W:
            string = W.read()

        # 有id
        match = re.search(r'mount-id\s+=([\s0-9,]*)', string)

        data_dict = {}
        if match:
            _id = match.group(1).replace(' ', '')
            _id = _id.replace('\n', '')
            _id = _id.replace('\r', '')
            _ids = _id.split(',')
            _id = _ids[0]
            file = 'H:\\gw2_2\\data\\mounts_skins\\mounts_skins_' + str(_id) + '.json'
            if os.path.exists(file):
                with open(file, 'r', encoding='utf8', newline='') as D:
                    data_dict = json.load(D)

        string = re.sub(r'\[\[(.*)]] is a \[\[(.*)]] \[\[mount]] skin.', r'[[\1]]是一个[[\2]]的[[坐骑]]皮肤。', string)
        # 处理链接
        string = wikiLinks3(string, _dict)
        # 处理h2、h3、h4
        string = re.sub(r'\=\=[\s]*Acquisition[\s]*\=\=', '== 获取方法 ==', string)
        string = re.sub(r'\=\=[\s]*Notes[\s]*\=\=', '== 注意 ==', string)
        string = string.replace('[[Category:Gem Store mounts]]', '[[category:宝石商店坐骑]]')
        string = string.replace('[[Griffon (mount)| 狮鹫]]', '[[狮鹫]]')
        string = string.replace('[[Raptor (mount)|肉食鸟]]', '[[肉食鸟]]')

        # 处理 infobox
        string, name, name_s, hasBracket, bracket = infoboxMount(string, w, data_dict)

        string = '{{需要翻译}}\n' + string + '[[category:搬运页面]][[category:坐骑]]\n'

        if 'name_zh' in data_dict:
            pageName = data_dict['name_zh']
        else:
            hasMatch, pageName = checkTranslation(name_s, _dict)
            if not hasMatch:
                print(pageName)

        fullPageName = pageName

        mountPage = site.pages[fullPageName]
        if mode == 'c':
            mountPage.save(string, summary='新坐骑页面', bot=True)

        print("mount page:", fullPageName, string)
        print("========================================================")


# 处理arena页面-特性相关
def processPageTraits(mode):
    pageNameSet = []
    r_log = ''
    p_log = ''
    error = ''
    p_list = []
    string = ''
    header_s = set()
    getRawFile('H:\\gw2_2\\wikiText\\en\\traits', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    for w in p_list:
        with open(w, 'r', encoding='utf8', newline='') as W:
            string = W.read()

        # 有id
        match = re.search(r'id\s+=([\s0-9,]*)', string)

        data_dict = {}
        if match:
            _id = match.group(1).replace(' ', '')
            _id = _id.replace('\n', '')
            _id = _id.replace('\r', '')
            _ids = _id.split(',')
            _id = _ids[0]
            file = 'H:\\gw2_2\\data\\v2_skills\\v2_traits_' + str(_id) + '.json'
            if os.path.exists(file):
                with open(file, 'r', encoding='utf8', newline='') as D:
                    data_dict = json.load(D)

        # 处理链接
        string = wikiLinks2(string, _dict)
        # 处理h2、h3、h4
        string = re.sub(r'\=\=[\s]*Related \[\[trait\]\]s[\s]*\=\=', '== 关联[[特性]] ==', string)
        string = re.sub(r'\=\=[\s]*Version history[\s]*\=\=', '== 版本历史 ==', string)
        string = re.sub(r'\=\=[\s]*Trivia[\s]*\=\=', '== 趣闻 ==', string)
        string = re.sub(r'\=\=[\s]*Notes[\s]*\=\=', '== 注意 ==', string)
        # 处理 infobox
        string, name, name_s, hasBracket, bracket = infoboxTrait(string, w, data_dict)

        string = '{{需要翻译}}\n' + string + '[[category:搬运页面]][[category:特性]]\n'

        hasMatch, pageName = checkTranslation(name_s, _dict)

        if not hasMatch:
            if 'name_zh' in data_dict:
                pageName = data_dict['name_zh']

        fullPageName = '特性/' + pageName
        # 有括号
        if hasBracket:
            match = re.search(r'id\s+=([\s0-9,]*)', string)
            # 有id
            if match:
                _id = match.group(1).replace(' ', '')
                _id = _id.replace('\n', '')
                _id = _id.replace('\r', '')
                _id = _id.replace('\t', '')
                _ids = _id.split(',')
                _id = _ids[0]
                if len(_ids) == 1:
                    fullPageName = fullPageName + '(' + _ids[0] + ')'
            # 没id
            else:
                fullPageName = fullPageName + '(' + bracket + ')'
        # 名字出现过（重名），准备消歧义:
        if fullPageName in pageNameSet:
            _suffix = w.split('\\')
            _suffix = _suffix[-1].replace('.wiki', '')
            _suffix = re.sub(r'\s(.*)', '', _suffix)
            fullPageName = fullPageName + '(' + _suffix + ')'
            error = error + fullPageName + ',' + w + '\n'
        # 创建重定向
        if match:
            for _i in _ids:
                _i = re.sub(r'\s', '', _i)
                r_name = 'Traits/' + str(_i)
                _r = site.pages[r_name]
                if mode == 'c':
                    _r.save('#重定向 [[' + fullPageName + ']]', summary='bot', bot=True)
                r_log = r_log + 'r:' + ',' + r_name + ',' + fullPageName + '\n'
                print('r_name updated:', r_name, fullPageName)
                print('-----------------------------')
        # 创建技能页面
        skillPage = site.pages[fullPageName]
        if mode == 'c':
            skillPage.save(string, summary='新技能页面', bot=True)
        pageNameSet.append(fullPageName)
        p_log = p_log + fullPageName + '\n'
        print("skill page updated:", fullPageName, string)
        print("========================================================")
    # 保存log
    logPath1 = 'H:\\gw2_2\\pageSkill.txt'
    with open(logPath1, 'w', encoding='utf8') as F:
        F.write(p_log)
    logPath2 = 'H:\\gw2_2\\redirectSkill.txt'
    with open(logPath2, 'w', encoding='utf8') as F:
        F.write(r_log)
    logPath3 = 'H:\\gw2_2\\errorSkill.txt'
    with open(logPath3, 'w', encoding='utf8') as F:
        F.write(error)


# 处理arena页面-技能相关
def processPageSkills(mode):
    pageNameSet = []
    r_log = ''
    p_log = ''
    error = ''
    p_list = []
    string = ''
    header_s = set()
    getRawFile('H:\\gw2_2\\wikiText\\en\\skills', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')
    for w in p_list:
        with open(w, 'r', encoding='utf8', newline='') as W:
            string = W.read()

        # 有id
        match = re.search(r'id\s+=([\s0-9,]*)', string)

        data_dict = {}
        if match:
            _id = match.group(1).replace(' ', '')
            _id = _id.replace('\n', '')
            _id = _id.replace('\r', '')
            _ids = _id.split(',')
            _id = _ids[0]
            file = 'H:\\gw2_2\\data\\v2_skills\\v2_skills_' + str(_id) + '.json'
            if os.path.exists(file):
                with open(file, 'r', encoding='utf8', newline='') as D:
                    data_dict = json.load(D)

        # 处理链接
        string = wikiLinks2(string, _dict)
        # 处理h2、h3、h4
        string = re.sub(r'\=\=[\s]*Related \[\[trait\]\]s[\s]*\=\=', '== 关联[[特性]] ==', string)
        string = re.sub(r'\=\=[\s]*Version history[\s]*\=\=', '== 版本历史 ==', string)
        string = re.sub(r'\=\=[\s]*Trivia[\s]*\=\=', '== 趣闻 ==', string)
        string = re.sub(r'\=\=[\s]*Notes[\s]*\=\=', '== 注意 ==', string)
        # 处理 infobox
        string, name, name_s, hasBracket, bracket = infoboxSkill(string, w, data_dict)

        string = '{{需要翻译}}\n' + string + '[[category:搬运页面]][[category:技能]]\n'

        hasMatch, pageName = checkTranslation(name_s, _dict)

        if not hasMatch:
            if 'name_zh' in data_dict:
                pageName = data_dict['name_zh']

        fullPageName = '技能/' + pageName
        # 有括号
        if hasBracket:
            match = re.search(r'id\s+=([\s0-9,]*)', string)
            # 有id
            if match:
                _id = match.group(1).replace(' ', '')
                _id = _id.replace('\n', '')
                _id = _id.replace('\r', '')
                _id = _id.replace('\t', '')
                _ids = _id.split(',')
                _id = _ids[0]
                if len(_ids) == 1:
                    fullPageName = fullPageName + '(' + _ids[0] + ')'
            # 没id
            else:
                fullPageName = fullPageName + '(' + bracket + ')'
        # 名字出现过（重名），准备消歧义:
        if fullPageName in pageNameSet:
            _suffix = w.split('\\')
            _suffix = _suffix[-1].replace('.wiki', '')
            _suffix = re.sub(r'\s(.*)', '', _suffix)
            fullPageName = fullPageName + '(' + _suffix + ')'
            error = error + fullPageName + ',' + w + '\n'
        # 创建重定向
        if match:
            for _i in _ids:
                _i = re.sub(r'\s', '', _i)
                r_name = 'Skills/' + str(_i)
                _r = site.pages[r_name]
                if mode == 'c':
                    _r.save('#重定向 [[' + fullPageName + ']]', summary='bot', bot=True)
                r_log = r_log + 'r:' + ',' + r_name + ',' + fullPageName + '\n'
                print('r_name updated:', r_name, fullPageName)
                print('-----------------------------')
        # 创建技能页面
        skillPage = site.pages[fullPageName]
        if mode == 'c':
            skillPage.save(string, summary='新技能页面', bot=True)
        elif mode == 'u':
            match = re.search(r'description\s+=(.*)', string)
            if match:
                if len(match.group()) > 1:
                    skillPage.save(string, summary='删除重复参数', bot=True)
                    print('correct description:', fullPageName)
        pageNameSet.append(fullPageName)
        p_log = p_log + fullPageName + '\n'
        # print("skill page updated:", fullPageName, string)
        print("========================================================")
    # 保存log
    logPath1 = 'H:\\gw2_2\\pageSkill.txt'
    with open(logPath1, 'w', encoding='utf8') as F:
        F.write(p_log)
    logPath2 = 'H:\\gw2_2\\redirectSkill.txt'
    with open(logPath2, 'w', encoding='utf8') as F:
        F.write(r_log)
    logPath3 = 'H:\\gw2_2\\errorSkill.txt'
    with open(logPath3, 'w', encoding='utf8') as F:
        F.write(error)


# 处理arena页面-物品的infobox
def infoboxItems(string, path, _data, _id, hasID):
    # add infobox skill
    string = re.sub(r'\{\{[\w]+ infobox', '{{infobox item', string)

    # 保留arena命名的英文名
    name = path.split('\\')
    name = name[-1].replace('.wiki', '')
    name = name.replace('%2F', "/")
    name = name.replace('%3A', ":")
    name = name.replace('%2A', "*")
    name = name.replace('%3F', "?")
    name = name.replace('%22', '"')

    name_s = name
    hasBracket = False
    bracket = ''
    name_match = re.search(r'\s\((.*\))', name)
    if name_match:
        # 不带括号的name en
        name_s = re.sub(r'(\s\(.*\))', '', name)
        hasBracket = True
        bracket = name_match.group(1)
    match1 = re.search('\| name\s=\s.*\n', string)
    if not match1:
        string = re.sub(r'{{infobox item', '{{infobox item\n| name = ' + name, string)

    # id
    match2 = hasID
    if match2:
        string = re.sub(r'\|\sid\s+=([\s0-9,]*)\n', '| id = ' + _id + '\n', string)
    else:
        string = re.sub(r'{{infobox item', '{{infobox item\n| id = ' + _id, string)

    # ask
    match4 = re.search(r'\{\{#ask:\[\[Has context::Item\]\]\[\[Has game id::[\d]+\]\]\|link=none\}\}', string)
    if match4:
        string = re.sub(r'\{\{#ask:\[\[Has context::Item\]\]\[\[Has game id::([\d]+)\]\]\|link=none\}\}',
                        r'{{recipe/id|\1}}', string)

    # description
    match3 = re.search(r'\| description\s=\s(.*)\n', string)

    if 'description_zh' in _data:
        if match3:
            string = re.sub(r'description\s=(.*)\n', 'description = ' + _data['description_zh'] + '\n',
                            string)
        else:
            string = re.sub(r'{{infobox item', '{{infobox item\n| description = ' + _data['description_zh'],
                            string)
    else:
        if match3:
            desc = match3.group(1).replace('\n', '')
            desc = desc.replace('\r', '')
            desc = re.sub(r'\[\[([\w\s\']*)\|[\w\s\']*\]\]', '\1', desc)
            desc = desc.replace('[', '')
            desc = desc.replace(']', '')
            hasMatch, transRes = checkTranslation(desc, _dict)
            # print('>>>>>>>>>>>>>>>>', desc, transRes)
            if hasMatch:
                string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + transRes + '\n',
                                string)
    if 'name_zh' in _data:
        string = re.sub(r'\{\{infobox\sitem', '{{infobox item\n| display_name_zh = ' + _data['name_zh'], string)
    else:
        _match1, res1 = checkTranslation(name_s, _dict)
        if _match1:
            string = re.sub(r'\{\{infobox item', '{{infobox item\n| display_name_zh = ' + res1, string)

    # remove interwiki
    string = re.sub(r'\[\[de\:.*\]\]', '', string)
    string = re.sub(r'\[\[es\:.*\]\]', '', string)
    string = re.sub(r'\[\[fr\:.*\]\]', '', string)
    string = re.sub(r'\[\[ru\:.*\]\]', '', string)

    # remove #ask:
    string = re.sub(r'(\{\{\#ask\:.*\}\})', r'<!--\1-->', string)

    return string, name, name_s, hasBracket, bracket


# 处理arena页面-坐骑通行证的infobox
def infoboxMountLcenses(string, path, _data):
    # add infobox skill
    string = re.sub(r'\{\{[iI]tem infobox', '{{infobox mount/license', string)

    # 保留arena命名的英文名
    name = path.split('\\')
    name = name[-1].replace('.wiki', '')
    name = name.replace('%2F', "/")
    name = name.replace('%3A', ":")
    name = name.replace('%2A', "*")
    name = name.replace('%3F', "?")
    name = name.replace('%22', '"')

    name_s = name
    hasBracket = False
    bracket = ''
    name_match = re.search(r'\s\((.*\))', name)
    if name_match:
        # 不带括号的name en
        name_s = re.sub(r'(\s\(.*\))', '', name)
        hasBracket = True
        bracket = name_match.group(1)

    match = re.search(r'\| name\s+=([\w\s\'\"\!]*)', string)
    if not match:
        string = re.sub(r'\{\{infobox mount/license', '{{infobox mount/license\n| name = ' + name, string)

    # description
    match = re.search(r'description\s+=\s(.*)\n', string)
    if 'description_zh' in _data:
        if match:
            string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + _data['description_zh'] + '\n',
                            string)
        else:
            string = re.sub(r'\{\{infobox mount/license',
                            '{{infobox mount/license\n| description = ' + _data['description_zh'],
                            string)
    else:
        if match:
            desc = match.group(1).replace('\n', '')
            desc = desc.replace('\r', '')
            desc = re.sub(r'\[\[([\w\s\']*)\|[\w\s\']*\]\]', '\1', desc)
            desc = desc.replace('[', '')
            desc = desc.replace(']', '')
            hasMatch, transRes = checkTranslation(desc, _dict)
            print('>>>>>>>>>>>>>>>>', desc, transRes)
            if hasMatch:
                string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + transRes + '\n',
                                string)
    if 'name_zh' in _data:
        string = re.sub(r'\{\{infobox mount/license',
                        '{{infobox mount/license\n| display_name_zh = ' + _data['name_zh'], string)
    else:
        _match1, res1 = checkTranslation(name_s, _dict)
        if _match1:
            string = re.sub(r'\{\{infobox mount/license', '{{infobox mount/license\n| display_name_zh = ' + res1,
                            string)

    # remove interwiki
    string = re.sub(r'\[\[[a-z]{2}\:.*\]\]', '', string)
    return string, name, name_s, hasBracket, bracket


# 处理arena页面-坐骑的infobox
def infoboxMount(string, path, _data):
    # add infobox skill
    string = re.sub(r'\{\{[iI]tem infobox', '{{infobox mount', string)

    # 保留arena命名的英文名
    name = path.split('\\')
    name = name[-1].replace('.wiki', '')
    name = name.replace('%2F', "/")
    name = name.replace('%3A', ":")
    name = name.replace('%2A', "*")
    name = name.replace('%3F', "?")
    name = name.replace('%22', '"')

    name_s = name
    hasBracket = False
    bracket = ''
    name_match = re.search(r'\s\((.*)\)', name)
    if name_match:
        # 不带括号的name en
        name_s = re.sub(r'(\s\(.*\))', '', name)
        hasBracket = True
        bracket = name_match.group(1)

    match = re.search(r'\| name\s=\s(.*)', string)
    if not match:
        string = re.sub(r'\{\{infobox mount', '{{infobox mount\n| name = ' + name, string)

    # description
    match = re.search(r'description\s+=\s(.*)\n', string)
    if 'description_zh' in _data:
        if match:
            string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + _data['description_zh'] + '\n',
                            string)
        else:
            string = re.sub(r'\{\{infobox mount', '{{infobox mount\n| description = ' + _data['description_zh'],
                            string)
    else:
        if match:
            desc = match.group(1).replace('\n', '')
            desc = desc.replace('\r', '')
            desc = re.sub(r'\[\[([\w\s\']*)\|[\w\s\']*\]\]', '\1', desc)
            desc = desc.replace('[', '')
            desc = desc.replace(']', '')
            hasMatch, transRes = checkTranslation(desc, _dict)
            print('>>>>>>>>>>>>>>>>', desc, transRes)
            if hasMatch:
                string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + transRes + '\n',
                                string)
    if 'name_zh' in _data:
        string = re.sub(r'\{\{infobox mount', '{{infobox mount\n| display_name_zh = ' + _data['name_zh'], string)
    else:
        _match1, res1 = checkTranslation(name_s, _dict)
        if _match1:
            string = re.sub(r'\{\{infobox mount', '{{infobox mount\n| display_name_zh = ' + res1, string)

    # remove interwiki
    string = re.sub(r'\[\[[a-z]{2}\:.*\]\]', '', string)
    return string, name, name_s, hasBracket, bracket


# 处理arena页面-特性的infobox
def infoboxTrait(string, path, _data):
    # 保留arena命名的英文名
    name = path.split('\\')
    name = name[-1].replace('.wiki', '')
    name = name.replace('%2F', "/")
    name = name.replace('%3A', ":")
    name = name.replace('%2A', "*")
    name = name.replace('%3F', "?")
    name = name.replace('%22', '"')

    name_s = name
    hasBracket = False
    bracket = ''
    name_match = re.search(r'\s\((.*\))', name)
    if name_match:
        name_s = re.sub(r'(\s\(.*\))', '', name)
        hasBracket = True
        bracket = name_match.group(1)

    match = re.search(r'name\s+=([\w\s\'\"\!]*)', string)
    if match:
        string = re.sub(r'name\s+=([\w\s\'\"\!]*)', 'name = ' + name, string)
    else:
        string = re.sub(r'\{\{Trait infobox', '{{Trait infobox\n| name = ' + name, string)

    # description

    match = re.search(r'description\s+=\s(.*)\n', string)
    if 'description_zh' in _data:
        string = re.sub(r'\{\{Trait infobox', '{{Trait infobox\n| description = ' + _data['description_zh'],
                        string)
    else:
        if match:
            desc = match.group(1).replace('\n', '')
            desc = desc.replace('\r', '')
            desc = re.sub(r'\[\[([\w\s\']*)\|[\w\s\']*\]\]', '\1', desc)
            desc = desc.replace('[', '')
            desc = desc.replace(']', '')
            hasMatch, transRes = checkTranslation(desc, _dict)
            print('>>>>>>>>>>>>>>>>', desc, transRes)
            if hasMatch:
                string = re.sub(r'\{\{Trait infobox', '{{Trait infobox\n| description = ' + transRes,
                                string)
    if 'name_zh' in _data:
        string = re.sub(r'\{\{Trait infobox', '{{Trait infobox\n| display_name_zh = ' + _data['name_zh'], string)
    else:
        _match1, res1 = checkTranslation(name_s, _dict)
        if _match1:
            string = re.sub(r'\{\{Trait infobox', '{{Trait infobox\n| display_name_zh = ' + res1, string)

    # remove interwiki
    string = re.sub(r'\[\[[a-z]{2}\:.*\]\]', '', string)
    return string, name, name_s, hasBracket, bracket


# 处理arena页面-技能的infobox
def infoboxSkill(string, path, _data):
    # add infobox skill
    string = re.sub(r'\{\{[sS]kill\sinfobox', '{{infobox skill', string)

    # 保留arena命名的英文名
    name = path.split('\\')
    name = name[-1].replace('.wiki', '')
    name = name.replace('%2F', "/")
    name = name.replace('%3A', ":")
    name = name.replace('%2A', "*")
    name = name.replace('%3F', "?")
    name = name.replace('%22', '"')

    name_s = name
    hasBracket = False
    bracket = ''
    name_match = re.search(r'\s\((.*\))', name)
    if name_match:
        name_s = re.sub(r'(\s\(.*\))', '', name)
        hasBracket = True
        bracket = name_match.group(1)

    match = re.search(r'name\s+=([\w\s\'\"\!]*)', string)
    if match:
        string = re.sub(r'name\s+=([\w\s\'\"\!]*)', 'name = ' + name, string)
    else:
        string = re.sub(r'\{\{infobox skill', '{{infobox skill\n| name = ' + name, string)

    # description

    match = re.search(r'description\s+=\s(.*)\n', string)
    if 'description_zh' in _data:
        if match:
            string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + _data['description_zh'] + '\n',
                            string)
        else:
            string = re.sub(r'\{\{infobox skill', '{{infobox skill\n| description = ' + _data['description_zh'],
                            string)
    else:
        if match:
            desc = match.group(1).replace('\n', '')
            desc = desc.replace('\r', '')
            desc = re.sub(r'\[\[([\w\s\']*)\|[\w\s\']*\]\]', '\1', desc)
            desc = desc.replace('[', '')
            desc = desc.replace(']', '')
            hasMatch, transRes = checkTranslation(desc, _dict)
            # print('>>>>>>>>>>>>>>>>', desc, transRes)
            if hasMatch:
                string = re.sub(r'description\s+=\s(.*)\n', 'description = ' + transRes + '\n',
                                string)
            else:
                string = re.sub(r'\{\{infobox skill', '{{infobox skill\n| description = ' + transRes,
                                string)
    if 'name_zh' in _data:
        string = re.sub(r'\{\{infobox skill', '{{infobox skill\n| display_name_zh = ' + _data['name_zh'], string)
    else:
        _match1, res1 = checkTranslation(name_s, _dict)
        if _match1:
            string = re.sub(r'\{\{infobox skill', '{{infobox skill\n| display_name_zh = ' + res1, string)

    # remove interwiki
    string = re.sub(r'\[\[[a-z]{2}\:.*\]\]', '', string)
    return string, name, name_s, hasBracket, bracket


def checkTranslationSkill(string, _dict):
    hasMatch = False
    transRes = string

    if string in _dict:
        hasMatch = True
        transRes = _dict[string]

    return hasMatch, transRes


def checkTranslation(string, _dict):
    hasMatch = False
    transRes = string

    for cat in _dict:
        if string in _dict[cat]:
            hasMatch = True
            transRes = _dict[cat][string]

    return hasMatch, transRes


# 翻译内链文字
def transLink(matched):
    s = matched.group(1)
    m = False

    strike = re.search(r'\|', s)
    if strike is not None:
        """
        寻找|左边的内容
        """
        match = re.search(r'(.*)\|(.*)', s)
        _l = match.group(1)
        _r = match.group(2)
        """
        翻译
        """
        hasMatch1, tRes1 = checkTranslation(_l, _dict)
        hasMatch2, tRes2 = checkTranslation(_r, _dict)
        res = '[[' + tRes1 + '|' + tRes2 + ']]'
        if hasMatch1:
            m = True

    else:
        hasMatch, tRes = checkTranslation(s, _dict)
        res = '[[' + tRes + ']]'
        if hasMatch:
            m = True
            if s not in TRANS:
                TRANS[s] = tRes

    # print('matched:', matched, res)
    return res


def wikiLinks2(string, _dict):
    res = re.sub(r'\[\[([^]]*)]]', transLink2, string)

    return res


def wikiLinks3(string):
    res = re.sub(r'\[\[([^]]*)]]', transLink, string)
    return res


def skillPath():
    with open('H:\\gw2_2\\dict.txt', 'r', encoding='utf8', newline='') as D:
        name_dict = json.load(D)
    p_list = []
    getRawFile('H:\\gw2_2\\data\\v2_skills', p_list, 'JSON')

    for p in p_list:
        with open(p, 'r', encoding='utf8', newline='') as D:
            data = json.load(D)
        skill_name_zh = data['name_zh']
        skill_name = data['name']

        site = Site('gw2.huijiwiki.com')
        site.login('报警机器人', ' ')

        _target = site.pages['技能/' + skill_name_zh]
        _redirect = site.pages['Skills/' + str(data['id'])]

        # 技能/中文名 存在
        if _target.exists:
            text = _target.text()
            match = re.search(r'(\|\s+name\s+=[\sa-zA-Z\',]*)', text)
            if match is None:
                text = re.sub(r'(\|\s+id\s+=[\s0-9,]*)', r"\1" + '| name = ' + data['name'] + '\n', text)
                _target.save(text, summary="更新", bot=True)
        else:
            text = '{{infobox skill\n|id = ' + str(data['id']) + '| name = ' + data['name'] + '\n}}\n'
            text = text + '[[category:搬运页面]][[category:技能]]'
            _target.save(text, summary="新建", bot=True)
            # print(text)
        # Skills/id 存在
        if _redirect.exists:
            text = _redirect.text()
            match = re.search(r'#重定向\s\[\[(.*)\]\]', text)
            if match:
                # Skills/id 指向的是错误的页面 【技能/中文名】
                if match.group(1) != '技能/' + skill_name_zh:
                    _wrong = site.pages[match.group(1)]
                    # 错误标题的页面存在
                    if _wrong.exists:
                        w_text = _wrong.text()
                        _match = re.search(r'id\s+=([\s0-9,]*)', w_text)
                        if _match:
                            __ids = _match.group(1).split(',')
                            # 错误标题的页面和正确页面的id一致
                            if str(data['id']) in __ids:
                                # 移动
                                if not _target.exists:
                                    _wrong.move('技能/' + skill_name_zh)
                                    print('moved:', match.group(1), '技能/' + skill_name_zh)
                                else:
                                    print('move failed(target exist):', match.group(1), '技能/' + skill_name_zh)
                                    _wrong.delete(reason='多余的页面')

                                print('correct:', 'Skills/' + str(data['id']) + '  -->', '技能/' + skill_name_zh)
                            # 错误标题的页面和正确页面的id不一致
                            else:
                                print("pending", data['id'], match.group(1), '技能/' + skill_name_zh)

                        # 不论目标页面是否存在，都订正重定向页面中 skill/id 的指向
                        _redirect.save('#重定向 [[' + '技能/' + skill_name_zh + ']]', reason="修订技能重定向")
        else:
            _redirect.save('#重定向 [[' + '技能/' + skill_name_zh + ']]', reason="添加技能重定向")
        sleep(2)


# 处理kzw给的中英对照表
def createDict():
    j__path = 'H:\\gw2_2\\dict\\JSON\\'
    c__path = 'H:\\gw2_2\\dict\\CSV\\'

    for c in _dict:
        c__path_2 = c__path + 'trans_' + str(c) + '.csv'

        if not os.path.exists(c__path_2):
            with open(c__path_2, 'w', newline='', encoding='utf_8_sig') as Csv:
                csv_header = ["en", "zh"]
                writer = csv.DictWriter(Csv, fieldnames=csv_header)

                writer.writeheader()
                for k in _dict[c]:
                    res = {'en': k, 'zh': _dict[c][k]}
                    writer.writerow(res)


def uploadsTrans():
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')
    res = '<table class="wikitable"><tr><th>分类</th><th>页面</th></tr>'
    j__path = 'H:\\gw2_2\\dict\\JSON\\'
    for c in _dict:
        print(c, type(c))
        j__path_2 = j__path + str(c) + '.json'

        if not os.path.exists(j__path_2):
            with open(j__path_2, 'w', encoding='utf8') as Dict:
                Dict.write(json.dumps(_dict[c], ensure_ascii=False))
            print(j__path_2)

        _list = [
            'Conversation',
            'Chatter',
            'Scene',
            'NPC',
            'Item',
            'Skill'
        ]

        if c not in _list:
            print('dui')
            text = json.dumps(_dict[c], ensure_ascii=False)
            page = site.pages['project:trans/' + str(c)]
            page.save(text, summary="更新词典", contentformat='application/json', contentmodel='json')
            res = res + '<tr><td>' + c + '</td><td>[[' + 'project:trans/' + str(c) + ']]</td></tr>'

    res = res + '<tr><td>Items</td> <td>[[' + 'project:trans/Items/1|project:trans/Items/1(A - L)]]</td></tr>'
    res = res + '<tr><td>Items</td> <td>[[' + 'project:trans/Items/2|project:trans/Items/1(续)]]</td></tr>'
    res = res + '<tr><td>Skills</td><td>[[' + 'project:trans/Skills/1|project:trans/Skills(A - L)]] </td></tr>'
    res = res + '<tr><td>Skills</td><td>[[' + 'project:trans/Skills/2|project:trans/Skills(续)]] </td></tr>'
    res = res + '</table>'
    _page = site.pages['project:trans']
    _page.save(res, summary="更新词典", )


def splitDict(_dict):
    res1 = {}
    res2 = {}
    _list = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'
    ]
    for k in _dict:

        if k != '':
            if str.lower(k[0]) in _list:
                res1[k] = _dict[k]
            else:
                res2[k] = _dict[k]

    return res1, res2


def uploadTrans2():
    item_list = []
    i_path = 'H:\\gw2_2\\localBulks\\v2_items'
    i_res = getDict(i_path)

    i_res1, i_res2 = splitDict(i_res)
    i_res1 = json.dumps(i_res1, ensure_ascii=False)
    i_res2 = json.dumps(i_res2, ensure_ascii=False)

    skill_list = []
    s_path = 'H:\\gw2_2\\localBulks\\v2_skills'
    s_res = getDict(s_path)

    s_res1, s_res2 = splitDict(s_res)
    s_res1 = json.dumps(s_res1, ensure_ascii=False)
    s_res2 = json.dumps(s_res2, ensure_ascii=False)

    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    i_page = site.pages['project:trans/Items/1']
    i_page.save(i_res1, summary="更新词典", contentformat='application/json', contentmodel='json')

    i_page = site.pages['project:trans/Items/2']
    i_page.save(i_res2, summary="更新词典", contentformat='application/json', contentmodel='json')

    s_page = site.pages['project:trans/Skills/1']
    s_page.save(s_res1, summary="更新词典", contentformat='application/json', contentmodel='json')

    s_page = site.pages['project:trans/Skills/2']
    s_page.save(s_res2, summary="更新词典", contentformat='application/json', contentmodel='json')

    print(i_res)


def getDict(_path):
    en_list = []
    zh_list = []

    en_dict = []
    zh_dict = []

    getRawFile(_path + '\\data', en_list, 'JSON')
    getRawFile(_path + '\\local', zh_list, 'JSON')

    for p in en_list:
        with open(p, mode='r', encoding='UTF-8') as F:
            # print(type(F))
            data = json.load(F)

            en_dict = en_dict + data

    # print('11',sub_cat, len(d_dict))  #

    for l in zh_list:
        with open(l, mode='r', encoding='UTF-8') as F:
            data = json.load(F)
            if 'zh' in data:
                data = data['zh']
                zh_dict = zh_dict + data
    res = {}
    for i in en_dict:
        e_id = i['id']
        if 'name' in i:
            for z in zh_dict:
                if e_id == z['id']:
                    if i['name'] not in res:
                        res[i['name']] = z['name']
                        # print(i['name'], z['name'])
    return res


def redirect():
    _list = {
        'Chapter 1: Searing Spell': '第1章：灼热法术',
        'Chapter 2: Igniting Burst': '第2章：引燃爆发',
        'Chapter 3: Heated Rebuke': '第3章：热力斥退',
        'Chapter 4: Scorched Aftermath': '第4章：战后焦土',
        'Epilogue: Ashes of the Just': '尾声：正义余烬',
        'Chapter 1: Desert Bloom': '第1章：沙漠之花',
        'Chapter 2: Radiant Recovery': '第2章：闪耀恢复',
        'Chapter 3: Azure Sun': '第3章：碧蓝之日',
        'Chapter 4: Shining River': '第4章：光耀河水',
        'Epilogue: Eternal Oasis': '尾声：永恒绿洲',
        'Chapter 1: Unflinching Charge': '第1章：坚定冲锋',
        'Chapter 2: Daring Challenge': '第2章：勇气挑战',
        'Chapter 3: Valiant Bulwark': '第3章：勇气壁垒',
        'Chapter 4: Stalwart Stand': '第4章：坚定不移',
        'Epilogue: Unbroken Lines': '尾声：牢固连结',
    }
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')
    for k in _list:
        # p = site.pages[k]
        # p.save('#重定向 [[' + '技能/' + _list[k] + ']]')

        _target = site.pages['技能/' + _list[k]]
        if _target.exists:
            text = _target.text()
            match = re.search(r'(\|\s+name\s+=[\sa-zA-Z\',]*)', text)
            if match is None:
                text = re.sub(r'(\|\s+id\s+=[\s0-9,]*)', r"\1" + '| name = ' + k + '\n', text)
                _target.save(text, summary="更新", bot=True)
            else:
                _target.save(text + '', summary="更新", bot=True)


# 维护- 手动翻译中文wiki的指定页面并把新获得的生词加入自动翻译对照表
def ManualTrans():
    page_list = [
        '冰巢传说',
        '世界动态',
        '世界动态第一季',
        '世界动态第二季',
        '世界动态第三季',
        '世界动态第四季',
        'Story characters',
    ]
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    for page in page_list:
        _page = site.pages[page]
        _text = _page.text()
        _text = wikiLinks3(_text, _dict)
        _page.save(_text, bot=True, summary='update trans')

    print(TRANS)

    trans_pairs = site.pages['MediaWiki:Huiji-translation-pairs']
    __text = trans_pairs.text()
    __dict = json.loads(__text, encoding='utf_8')

    for item in TRANS:
        if item not in __dict['link']:
            __dict['link'][item] = TRANS[item]
    print(__dict)

    trans_pairs.save(json.dumps(__dict, ensure_ascii=False), bot=True, summary='update')


def blog(mode):
    p_list = []
    getRawFile('H:\\gw2_2\\wikiText\\en\\items', p_list, 'WIKI')
    site = Site('gw2.huijiwiki.com')
    site.login('报警机器人', ' ')

    w = 'H:\\gw2_2\\wikiText\\en\\items\\Studded Pants.wiki'
    with open(w, 'r', encoding='utf8', newline='') as W:
        _string = W.read()
    # 移除注释
    _string = re.sub(r'\<!--(.*)--\>', '', _string)

    # get subcategory
    subcategory = ''
    subcategory_m = re.search(r'\{\{([\w\s]+) infobox', _string)
    if subcategory_m:
        subcategory = subcategory_m.group(1)

    # id
    id_match, matched_id = arena_find_id(_string)
    # isHistorical
    historical = re.search(r'\| status = historical', _string)

    _items = [
        "item",
        "weapon",
        "dye",
        "inventory",
        "armor",
        "trinket",
        "upgrade component",
        "back item"
    ]
    _excluded = [
        'dye',
        'skin'
    ]
    if subcategory.lower() in _items:
        data_dict = {}
        # 历史物品
        if historical is None:
            # 有id
            if id_match:
                _ids = matched_id.replace(' ', '')
                _ids = _ids.replace('\n', '')
                _ids = _ids.replace('\r', '')
                _ids = _ids.replace('\t', '')
                # 可能有多个id
                _ids = _ids.split(',')
                for _id in _ids:
                    if _id != '':
                        file = 'H:\\gw2_2\\data\\v2_items\\v2_items_' + str(_id) + '.json'
                        if os.path.exists(file):
                            with open(file, 'r', encoding='utf8', newline='') as D:
                                data_dict = json.load(D)

                        string = _string
                        # 处理链接
                        string, name, name_s, hasBracket, bracket = process_items_content(string, w, data_dict, _id)

                        if 'name_zh' in data_dict:
                            pageName = data_dict['name_zh']
                        else:
                            hasMatch, pageName = checkTranslation(name_s, _dict)

                        fullPageName = pageName
                        # 有括号
                        if hasBracket:
                            match = re.search(r'id\s+=([\s0-9,]*)', string)
                            # 有id
                            if match:
                                fullPageName = fullPageName + '(' + bracket + ')'

                        # mountPage = site.pages[fullPageName]
                        if mode == 'c':
                            pass
                            # mountPage.save(string, summary='新坐骑领养证页面', bot=True)
                        elif mode == 'l':
                            new_name = w.split('\\')
                            new_name = new_name[-1]

                            path = 'H:\\gw2_2\\wikiText\\zh\\items\\'

                            # 名字里是否包含 #
                            match = re.search('#', new_name)

                            print("item page:", fullPageName, _id, string)

                            print("========================================================")
            # 没有id
            else:
                # print(w)
                new_name = w.split('\\')
                new_name = new_name[-1]
                # 名字里是否包含 #
                match = re.search('#', new_name)
                # 有# 是子页面（无需保存文件）
                if match is not None:
                    if os.path.exists('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name):
                        os.remove('H:\\gw2_2\\wikiText\\zh\\items no id\\' + new_name)
                # 没有# 不是子页面
                else:
                    __ids = itemsProcessReturnID(_string, w)
                    # 至少包含1个有效的id
                    if len(__ids) > 0:
                        for __id in __ids:
                            string = _string
                            string, name, name_s, hasBracket, bracket = process_items_content(string, w, data_dict,
                                                                                              __id)

                            print(">>>:", __id, name, string)
                    # 一个id都没有
                    else:

                        string, name, name_s, hasBracket, bracket = process_items_content(_string, w, data_dict, '')

                        print("]]]:", new_name, string)
        else:

            new_name = w.split('\\')
            new_name = new_name[-1]
            string, name, name_s, hasBracket, bracket = process_items_content(_string, w, data_dict, '')


# processPage()

# skillPath()
# uploadsTrans()
# uploadTrans2()
# redirect()
# checkPetSkill()
# processPageSkills(mode='u')
# processPageTraits(mode='c')
# ManualTrans()
# processPageMount(mode='c')
# processPageMountLisence(mode='c')
# delete()
# preprocessPageItems()
processPageItems(mode='l')
updatePageItems(mode='c')
# blog(mode='l')
