# -*- coding: utf-8 -*-
'''PVF 编辑器搜索面板自检：不依赖数据库/PVF 文件，用假数据验证
"筛选 -> 结果树 -> 选中 -> 提交回调"整条链，以及两个 tab 的面板是否都在。

跑法：.venv\\Scripts\\python.exe tests\\editor_search_check.py
'''
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dnfpkgtool import cacheManager as cacheM
from dnfpkgtool import pvfEditorGUI


def main():
    fake = {
        1001: {'[minimum level]': [5], '[rarity]': [4], '[stackable type]': ['[consumable]']},
        1002: {'[minimum level]': [-1]},
        1003: {'[minimum level]': [70], '[rarity]': [5], '[stackable type]': ['[material]']},
    }
    names = {1001: '小红药', 1002: '无色小晶块', 1003: '史诗巨剑'}
    cacheM.get_Item_Info_In_Dict = lambda itemID, cacheDict=None: fake.get(itemID, {})
    cacheM.stackableDict = names
    cacheM.ITEMS_dict = names

    root = tk.Tk()
    root.withdraw()
    failed = []

    def check(name, cond, extra=''):
        print(('  OK   ' if cond else '  FAIL ') + name + (f'  {extra}' if extra else ''))
        if not cond:
            failed.append(name)

    app = pvfEditorGUI.PvfeditmainframeApp(root)
    panel = app.stkTab.searchPanel
    check('道具 tab 有搜索面板', panel is not None and panel.isEquipment is False)
    check('装备 tab 有搜索面板', app.equTab.searchPanel is not None and app.equTab.searchPanel.isEquipment is True)
    check('面板有 5 列结果树', len(panel.resultTree['columns']) == 5)

    submitted = []
    panel._submit(lambda itemID: submitted.append(itemID))
    check('未选中时不提交', submitted == [])

    panel.run_Search()
    rows = panel.resultTree.get_children()
    check('无条件搜索出全部道具', len(rows) == 3, f'rows={len(rows)}')

    panel.nameE.insert(0, '红药')
    panel.fuzzyVar.set(1)
    panel.run_Search()
    rows = panel.resultTree.get_children()
    check('关键词搜索', len(rows) == 1, f'rows={len(rows)}')
    check('结果行带等级/稀有度', list(panel.resultTree.item(rows[0])['values'])[3:] == [5, cacheM.rarityMap[4]],
          str(panel.resultTree.item(rows[0])['values']))

    picked = []
    panel.onPick = lambda itemID: picked.append(itemID)
    panel.resultTree.focus(rows[0])
    panel._select_Result()
    check('选中回填回调', picked == [1001], str(picked))
    check('回填到 ID 框', panel.resultTree.item(rows[0])['values'][0] == 1001)

    panel._submit(lambda itemID: submitted.append(itemID))
    check('提交回调拿到 itemID', submitted == [1001], str(submitted))

    panel.nameE.delete(0, tk.END)
    panel.fuzzyVar.set(0)
    panel.minLevE.insert(0, '60')
    panel.run_Search()
    check('等级下限筛选', [panel.resultTree.item(i)['values'][0] for i in panel.resultTree.get_children()] == [1003])

    # 装备分支：三级分类不选时用全量装备字典，且稀有度带"时装"后缀
    equFake = {2001: {'[minimum level]': [95], '[rarity]': [6], '[equipment type]': ['[weapon]']},
               2002: {'[minimum level]': [10], '[rarity]': [4], 'avatar': True, '[stackable type]': ['[avatar]']}}
    cacheM.get_Item_Info_In_Dict = lambda itemID, cacheDict=None: (fake | equFake).get(itemID, {})
    cacheM.equipmentDict = {2001: '沧海巨剑', 2002: '天四时装上衣'}
    equPanel = app.equTab.searchPanel
    equPanel.run_Search()
    equRows = [list(equPanel.resultTree.item(i)['values']) for i in equPanel.resultTree.get_children()]
    check('装备搜索出全部装备', len(equRows) == 2, str(equRows))
    check('时装稀有度带后缀', [row[4] for row in equRows if row[0] == 2002] == [cacheM.rarityMap[4] + '时装'], str(equRows))
    equPanel.rarityE.set(cacheM.rarityMap[6])
    equPanel.run_Search()
    check('装备稀有度筛选', [equPanel.resultTree.item(i)['values'][0] for i in equPanel.resultTree.get_children()] == [2001])

    check('按标签名切 tab', app.select_Tab('装备') is True and app.tabView.tab(app.tabView.select(), 'text').strip() == '装备')
    check('未知标签名不切', app.select_Tab('不存在') is False)

    # 共用背包编辑器的 PVF：不弹文件框、沿用背包的路径与编码
    import tempfile, threading
    called = {}
    gate = threading.Event()

    def fake_load(usePVF=False, pvfPath='', *a, **kw):
        called['path'] = str(pvfPath)
        called['ret'] = kw.get('retType')
        called['enc'] = kw.get('encode')
        gate.set()
        raise RuntimeError('__stop_here__')      # 假 PVF 撑不到后面，直接中断

    def fake_dialog(**kw):
        called['dialog'] = True
        return ''

    tmp = ROOT / '_shared_pvf_test.pvf'
    tmp.write_bytes(b'x')
    cacheM.loadItems2 = fake_load
    pvfEditorGUI.askopenfilename = fake_dialog
    cacheM.PVFcacheDict['pvfPath'] = str(tmp)
    cacheM.PVFcacheDict['encode'] = 'gbk'
    root.after(50, app.open_PVF)          # 子线程会更新控件，需要有 mainloop
    root.after(2500, root.quit)
    root.mainloop()
    check('等待到加载调用', gate.wait(3), str(called))
    check('复用背包编辑器的 PVF 路径', called.get('path') == str(tmp), str(called))
    check('不再弹文件选择框', 'dialog' not in called)
    check('编码跟随背包缓存', called.get('enc') == 'gbk', str(called.get('enc')))
    check('工具栏不再有加载PVF控件', not hasattr(app, 'openPVGBtn') and not hasattr(app, 'PVFE') and not hasattr(app, 'encodeE'))
    check('编辑器不再自带日志控件', not hasattr(app, 'logE') and hasattr(app, 'logFunc'))
    tmp.unlink()

    root.destroy()
    if failed:
        print('EDITOR_SEARCH_CHECK FAILED:', failed)
        return 1
    print('EDITOR_SEARCH_CHECK PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
