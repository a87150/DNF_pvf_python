# 搜索合并自检：搜索面板的"载入修改"必须能直接填进背包的修改物品控件
import sys, os, tkinter as tk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dnfpkgtool import pvfEditorGUI as E
import dnfpkgtool.__main__ as M

def check(name, cond):
    print(('PASS  ' if cond else 'FAIL  ') + name)
    if not cond:
        sys.exit(1)

root = tk.Tk(); root.withdraw()
hits = []
panel = E.ItemSearchPanel(root, isEquipment=False,
                          onLoadEdit=hits.append,
                          onSubmitBag=lambda i: None, onSubmitMail=lambda i: None)

def texts(w, out=None):
    out = [] if out is None else out
    for c in w.winfo_children():
        try:
            if 'text' in c.keys():
                out.append(c.cget('text'))
        except Exception:
            pass
        texts(c, out)
    return out

btns = texts(panel)
check('搜索面板有"修改物品数据"按钮', '修改物品数据' in btns)
check('三个按钮都在(提交编辑/提交邮件/修改物品数据)', all(t in btns for t in ('提交编辑', '提交邮件', '修改物品数据')))
check('按钮顺序为 提交编辑->提交邮件->修改物品数据', [t for t in btns if t in ('提交编辑', '提交邮件', '修改物品数据')] == ['提交编辑', '提交邮件', '修改物品数据'])
check('onLoadEdit 已保存', panel.onLoadEdit is not None)
panel.selected_ID = lambda: 777          # 模拟选中结果
panel._submit(panel.onLoadEdit)
check('点按钮会把选中物品ID交给回调', hits == [777])
panel.selected_ID = lambda: None
panel.onLoadEdit = None
panel._submit(panel.onLoadEdit)          # 没回调也不能炸
check('无回调时安全', True)

check('主窗口实现了 submit_Search_to_Edit', hasattr(M.GuiApp, 'submit_Search_to_Edit'))
src1 = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dnfpkgtool', 'guiActions.py'), 'rb').read().decode('utf-8')
src2 = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dnfpkgtool', 'guiTabMain.py'), 'rb').read().decode('utf-8')
check('编辑器打开时传入了 onLoadEdit', 'onLoadEdit=self.submit_Search_to_Edit' in src1)
check('物品编辑控件已按页签登记', 'itemEditFrameDict[tabName] = itemEditFrame' in src2)
check('载入修改会写入物品ID/名称', 'itemEditFrame.itemIDEntry.insert(0,itemID)' in src1 and 'itemEditFrame.itemNameEntry.insert' in src1)
root.destroy()
print('SEARCH_MERGE_CHECK PASSED')
