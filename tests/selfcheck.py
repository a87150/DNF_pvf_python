# -*- coding: utf-8 -*-
"""最小自检：三条不依赖数据库/PVF 的断言，跑通即说明核心字节逻辑与 L2 重构没坏。

用法（任意目录均可）：
    .venv\\Scripts\\python.exe tests\\selfcheck.py
"""
import os
import sys
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)                      # 各模块按 ./config/*.json 取数据，必须从仓库根运行
sys.path.insert(0, ROOT)

from dnfpkgtool import pvfEditor, pvfReader, cacheManager, sqlManager2


def check_pvf_crypto():
    """PVF 头部/文件块的加解密必须互逆（长度取 4 的倍数）"""
    for size, crc in ((4096, 0x81A79011), (1024, 0x12345678)):
        data = bytes(random.getrandbits(8) for _ in range(size))
        assert pvfReader.decrypt_Bytes(pvfEditor.encrypt_Bytes(data, crc), crc) == data
        assert pvfEditor.encrypt_Bytes(pvfReader.decrypt_Bytes(data, crc), crc) == data
    return "PVF 加解密往返"


def check_item_slot():
    """物品格子 blob：解析 -> 重建 -> 再解析，字段必须一致"""
    blob = bytearray(61)
    blob[1] = 0x01                                # 装备
    blob[2:6] = (12345).to_bytes(4, 'little')     # itemID
    blob[6] = 0x0C | (2 << 5)                     # 强化 +12，封印次数 2
    blob[7:11] = (3).to_bytes(4, 'big')           # 品级（装备为大端）
    item = sqlManager2.DnfItemSlot(bytes(blob))
    assert (item.type, item.id) == (0x01, 12345)
    assert (item.enhancementLevel, item.sealCnt) == (12, 2)
    again = sqlManager2.DnfItemSlot(item.build_bytes())
    for field in ('type', 'id', 'enhancementLevel', 'sealCnt', 'num_grade', 'durability'):
        assert getattr(again, field) == getattr(item, field), field
    return "物品 blob 解析/重建"


def check_lev_rarity():
    """L2 抽出的 get_lev_rarity：缺字段给默认值，有字段走映射"""
    assert cacheManager.get_lev_rarity({}) == (0, '')
    assert cacheManager.get_lev_rarity({'[minimum level]': [55]}) == (55, '')
    assert cacheManager.get_lev_rarity({'[rarity]': [3]}) == (0, '神器')
    assert cacheManager.get_lev_rarity({'[minimum level]': [55], '[rarity]': [3]}) == (55, '神器')
    return "get_lev_rarity 默认值/映射"


def check_rarity_single_source():
    """rarityMap 只保留一份，其余模块必须引用同一个对象"""
    from dnfpkgtool import pvfCacheFrame, pvfEditorGUI
    assert pvfCacheFrame.rarityMap is cacheManager.rarityMap
    assert pvfEditorGUI.rarityMap is cacheManager.rarityMap
    assert (cacheManager.rarityMap[2], cacheManager.rarityMapRev['稀有']) == ('稀有', 2)
    return "rarityMap 单源"


def check_search_items():
    """共享筛选函数：关键词 / 等级 / 稀有度 / 归一 / 时装后缀 / 条数上限"""
    fake = {
        1001: {'[minimum level]': [5], '[rarity]': [4]},
        1002: {'[minimum level]': [-1]},
        1003: {'[minimum level]': [70], '[rarity]': [5]},
    }
    names = {1001: '小红药', 1002: '无色小晶块', 1003: '史诗巨剑'}
    real = cacheManager.get_Item_Info_In_Dict
    cacheManager.get_Item_Info_In_Dict = lambda itemID, cacheDict=None: fake.get(itemID, {})
    try:
        ids = lambda res: [r[0] for r in res]
        assert ids(cacheManager.search_Items(names, '红药', fuzzy=True)) == [1001]
        assert ids(cacheManager.search_Items(names, levMin=60)) == [1003]
        assert ids(cacheManager.search_Items(names, levMin=0)) == [1001, 1003]        # -1 级默认排除
        assert ids(cacheManager.search_Items(names, levMin=0, normalize=True)) == [1001, 1002, 1003]
        assert ids(cacheManager.search_Items(names, rarity=cacheManager.rarityMap[5])) == [1003]
        # 上限在筛选之前截断（与原逻辑一致），故配合 normalize 才能凑满 2 条
        assert len(cacheManager.search_Items(names, limit=2, normalize=True)) == 2
        assert cacheManager.search_Items(names, levMin=71) == []
        fake[1001]['[equipment type]'] = ['[coat]']
        suffix = lambda d: '时装' if d.get('[equipment type]') else ''
        assert ids(cacheManager.search_Items(names, rarity=cacheManager.rarityMap[4] + '时装',
                                             raritySuffix=suffix)) == [1001]
    finally:
        cacheManager.get_Item_Info_In_Dict = real
    return "search_Items 关键词/等级/稀有度/归一/时装/上限"


if __name__ == '__main__':
    failed = 0
    for fn in (check_pvf_crypto, check_item_slot, check_lev_rarity, check_rarity_single_source,
               check_search_items):
        try:
            print(f'[OK]   {fn.__name__}: {fn()}')
        except Exception as e:
            failed += 1
            print(f'[FAIL] {fn.__name__}: {type(e).__name__}: {e}')
    print('SELFCHECK', 'FAILED' if failed else 'PASSED')
    sys.exit(1 if failed else 0)
