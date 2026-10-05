# -*- coding: utf-8 -*-
'''PVF 编辑器「修改物品数据」按钮自检：结果树选中 -> _submit -> onEditData -> 右侧面板填充。

修复前的两个 bug 都会被这里的断言打到：
  1) btn_edit_file/btn_edit_with_new_file 不收 itemID，_submit 传参即 TypeError（Tk 吞掉，界面无反应）
  2) selected_ID 只看 focus 行，selection_set 选中的行取不到

跑法：.venv\\Scripts\\python.exe tests\\editor_editbutton_check.py
'''
import copy
import sys
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dnfpkgtool import cacheManager as cacheM
from dnfpkgtool import pvfEditorGUI as E

ITEM_ID = 4812
ITEM_NAME = '废旧电池'
ROW = (ITEM_ID, ITEM_NAME, '任务材料', 1, '神器')
ITEM_DICT = {
    '[name]': [ITEM_NAME],
    '[stackable type]': ['[material]', 0],
    '[minimum level]': [1],
    '[rarity]': [4],
}


class FakePVF:
    '''只实现 btn_edit_* 实际用到的那几个 PVF 接口'''
    def __init__(self, basePath):
        self.filePath = basePath
        self.fileTreeDict = {basePath: {'filePath': basePath}}

    def itemID2itemPath(self, itemID, lst=None):
        return self.filePath

    def read_File_In_Dict(self, filePath):
        return copy.deepcopy(ITEM_DICT)


def add_row(panel):
    return panel.resultTree.insert('', tk.END, values=ROW)


def main():
    # 按 tests/editor_search_check.py 的做法准备 cacheM（不碰数据库/PVF 文件）
    cacheM.stackableDict = {ITEM_ID: ITEM_NAME}
    cacheM.equipmentDict = {ITEM_ID: ITEM_NAME}

    root = tk.Tk()
    root.withdraw()
    failed = []

    def check(name, cond, extra=''):
        print(('  OK   ' if cond else '  FAIL ') + name + (f'  {extra}' if extra else ''))
        if not cond:
            failed.append(name)

    def no_raise(name, fn):
        try:
            fn()
            check(name, True)
        except Exception as e:
            check(name, False, f'{type(e).__name__}: {e}')

    stk = E.PvfeditstackableframeWidget(root)
    equ = E.PvfeditequipmentframeWidget(root)
    stk.pvf = FakePVF('stackable/4812.stk')
    equ.pvf = FakePVF('equipment/4812.equ')
    check('两个 tab 的 onEditData 都接在 btn_edit_file 上',
          stk.searchPanel.onEditData == stk.btn_edit_file and equ.searchPanel.onEditData == equ.btn_edit_file)

    # --- 断言1：选中行（selection+focus）后点「修改物品数据」不再 TypeError ---
    tree = stk.searchPanel.resultTree
    iid = add_row(stk.searchPanel)
    tree.selection_set(iid)
    tree.focus(iid)
    no_raise('断言1 _submit(onEditData) 不抛异常', lambda: stk.searchPanel._submit(stk.searchPanel.onEditData))

    # --- 断言3：真实 onEditData 之后右侧面板确实被填上了内容 ---
    check('断言3 右侧文件路径被填充', stk.filePathE.get() == 'stackable/4812.stk', repr(stk.filePathE.get()))
    check('断言3 右侧名称被填充', stk.nameE.get() == ITEM_NAME, repr(stk.nameE.get()))

    # --- 断言2：只 selection_set、不给 keyboard focus，spy 也要收到 int itemID ---
    got = []
    spyPanel = E.ItemSearchPanel(root, isEquipment=False, onEditData=got.append)
    sid = add_row(spyPanel)
    spyPanel.resultTree.selection_set(sid)
    check('断言2 selected_ID 优先取 selection()', spyPanel.selected_ID() == ITEM_ID, repr(spyPanel.selected_ID()))
    spyPanel._submit(spyPanel.onEditData)
    check('断言2 spy 收到 int itemID', got == [ITEM_ID] and type(got[0]) is int, str(got))

    spyPanel.resultTree.selection_remove(sid)
    spyPanel.resultTree.focus(sid)
    check('断言2 selection 为空时退回 focus()', spyPanel.selected_ID() == ITEM_ID, repr(spyPanel.selected_ID()))

    # --- 断言4：没选中任何行 / 传 None 都不抛异常 ---
    spyPanel.resultTree.selection_remove(sid)
    spyPanel.resultTree.focus('')
    check('断言4 无选中时 selected_ID 返回 None', spyPanel.selected_ID() is None, repr(spyPanel.selected_ID()))
    no_raise('断言4 无选中时 _submit 不抛异常', lambda: spyPanel._submit(spyPanel.onEditData))
    check('断言4 spy 没收到任何 ID', got == [ITEM_ID], str(got))
    stk.searchPanel.resultTree.selection_remove(*stk.searchPanel.resultTree.selection())
    stk.searchPanel.resultTree.focus('')
    no_raise('断言4 btn_edit_file() 无选中不抛异常', lambda: stk.btn_edit_file())
    no_raise('断言4 btn_edit_file(None) 无选中不抛异常', lambda: stk.btn_edit_file(None))
    no_raise('断言4 btn_edit_with_new_file() 无选中不抛异常', lambda: equ.btn_edit_with_new_file())
    check('断言4 无选中时返回 False', stk.btn_edit_file() is False and equ.btn_edit_with_new_file() is False)

    # --- 四个方法都接受显式 itemID 并载入右侧 ---
    for label, widget, path in (('道具', stk, 'stackable/4812.stk'), ('装备', equ, 'equipment/4812.equ')):
        widget.btn_edit_file(ITEM_ID)
        check(f'{label} btn_edit_file(itemID) 载入右侧', widget.filePathE.get() == path and widget.nameE.get() == ITEM_NAME,
              repr((widget.filePathE.get(), widget.nameE.get())))
        widget.btn_edit_with_new_file(ITEM_ID)   # 新文件：右侧只挂目录名 + [新]名称
        check(f'{label} btn_edit_with_new_file(itemID) 载入右侧',
              widget.filePathE.get() == path.split('/')[0] + '/' and widget.nameE.get() == '[新]' + ITEM_NAME,
              repr((widget.filePathE.get(), widget.nameE.get())))

    root.destroy()
    if failed:
        print('EDITOR_EDITBUTTON_CHECK FAILED:', failed)
        return 1
    print('EDITOR_EDITBUTTON_CHECK PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
