# 搜索合并自检：左侧 = 一个搜索栏 + 一个结果列表 + 四个按钮
# 四个按钮依次为 提交编辑 -> 提交邮件 -> 修改物品数据 -> 以该物品为模板
import sys, os, tkinter as tk
from tkinter import ttk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dnfpkgtool import pvfEditorGUI as E

EXPECTED = ['提交编辑', '提交邮件', '修改物品数据', '以该物品为模板']

def check(name, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + (f'  {extra}' if extra else ''))
    if not cond:
        sys.exit(1)

root = tk.Tk(); root.withdraw()
hits = {}
def record(key):
    return lambda itemID: hits.setdefault(key, []).append(itemID)

panel = E.ItemSearchPanel(root, isEquipment=False,
                          onSubmitBag=record('bag'), onSubmitMail=record('mail'),
                          onEditData=record('edit'), onTemplate=record('tpl'))

def buttons(w, out=None):
    out = [] if out is None else out
    for c in w.winfo_children():
        if isinstance(c, ttk.Button):
            out.append(c)
        buttons(c, out)
    return out

btns = buttons(panel)
texts = [b.cget('text') for b in btns]
check('四个按钮都在(提交编辑/提交邮件/修改物品数据/以该物品为模板)', all(t in texts for t in EXPECTED))
check('按钮顺序为 提交编辑->提交邮件->修改物品数据->以该物品为模板',
      [t for t in texts if t in EXPECTED] == EXPECTED)
check('onEditData 已保存', panel.onEditData is not None)
check('onTemplate 已保存', panel.onTemplate is not None)
check('旧参数 onLoadEdit 已删除', not hasattr(panel, 'onLoadEdit'))

panel.selected_ID = lambda: 777          # 模拟选中结果
for b in btns:
    b.invoke()
check('点四个按钮把选中物品ID交给各自回调',
      [hits.get(k) for k in ('bag', 'mail', 'edit', 'tpl')] == [[777]] * 4, str(hits))

panel.selected_ID = lambda: None         # 未选中
for b in btns:
    b.invoke()
check('selected_ID 返回 None 时点按钮不炸', True)

for key in ('onSubmitBag', 'onSubmitMail', 'onEditData', 'onTemplate'):
    setattr(panel, key, None)
for b in btns:
    b.invoke()
check('无回调时安全', True)

root.destroy()
print('SEARCH_MERGE_CHECK PASSED')
