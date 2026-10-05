'''主窗口初始化与整体布局（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppInit:
    def __init__(self, master=None, check_update=True,style=None):
        # build ui
        self.mainFrame = ttk.Frame(master)
        self.mainFrame.configure(height=500, width=700)
        frame2 = ttk.Frame(self.mainFrame)
        frame2.configure(height=200, width=200)
        label1 = ttk.Label(frame2)
        label1.configure(text='数据库IP')
        label1.pack(padx=3, side="left")
        self.db_ipE = ttk.Combobox(frame2)
        self.db_ipE.pack(expand=True, fill="x", side="left")
        self.db_ipE.bind("<<ComboboxSelected>>", self.sel_IP, add="")
        label2 = ttk.Label(frame2)
        label2.configure(text='端口')
        label2.pack(padx=3, side="left")
        self.db_portE = ttk.Entry(frame2)
        self.db_portE.configure(width=8)
        self.db_portE.pack(expand=True, fill="x", side="left")
        label3 = ttk.Label(frame2)
        label3.configure(text='用户名')
        label3.pack(padx=3, side="left")
        self.db_userE = ttk.Entry(frame2)
        self.db_userE.configure(width=10)
        self.db_userE.pack(expand=True, fill="x", side="left")
        label4 = ttk.Label(frame2)
        label4.configure(text='密码')
        label4.pack(padx=3, side="left")
        self.db_pwdE = ttk.Combobox(frame2)
        self.db_pwdE.configure(width=10)
        self.db_pwdE.pack(expand=True, fill="x", side="left")
        self.db_conBTN = ttk.Button(frame2)
        self.db_conBTN.configure(text='连接数据库')
        self.db_conBTN.pack(expand=True, fill="x", padx=3, side="left")
        self.db_conBTN.configure(command=self.connectSQL)
        frame2.pack(fill="x", side="top")
        separator1 = ttk.Separator(self.mainFrame)
        separator1.configure(orient="horizontal")
        separator1.pack(fill="x", pady=3, side="top")
        self.tabFrame = ttk.Frame(self.mainFrame)
        self.tabFrame.configure(height=450, width=200)
        self.tabView = ttk.Notebook(self.tabFrame)
        self.tabView.configure(height=400, width=800)
        self.searchFrame = ttk.Frame(self.tabView)
        self.searchFrame.configure(height=200, width=200)
        frame13 = ttk.Frame(self.searchFrame)
        frame13.configure(height=200, width=200)
        labelframe1 = ttk.Labelframe(frame13)
        labelframe1.configure(height=200, text='账户查询', width=200)
        self.aNameE = ttk.Entry(labelframe1)
        self.aNameE.configure(width=15)
        self.aNameE.pack(expand=False, pady=1, side="top")
        self.accountSearchBtn = ttk.Button(labelframe1)
        self.accountSearchBtn.configure(state="disabled", text='查询/加载所有')
        self.accountSearchBtn.pack(expand=False, fill="x", pady=1, side="top")
        self.accountSearchBtn.configure(command=self.search_Account)
        labelframe1.pack(expand=True, fill="both", side="top")
        labelframe4 = ttk.Labelframe(frame13)
        labelframe4.configure(height=200, text='角色查询', width=200)
        self.cNameE = ttk.Entry(labelframe4)
        self.cNameE.configure(width=15)
        self.cNameE.pack(expand=False, pady=1, side="top")
        self.characSearchBtn = ttk.Button(labelframe4)
        self.characSearchBtn.configure(state="disabled", text='查询/加载在线')
        self.characSearchBtn.pack(expand=False, fill="x", pady=1, side="top")
        self.characSearchBtn.configure(command=self.search_Charac)
        labelframe4.pack(expand=True, fill="both", side="top")
        labelframe5 = ttk.Labelframe(frame13)
        labelframe5.configure(height=200, text='角色显示及编码', width=200)
        self.connectorE = ttk.Combobox(labelframe5)
        self.connectorE.configure(width=10)
        self.connectorE.pack(expand=False, fill="x", pady=1, side="top")
        self.SqlEncodeE = ttk.Combobox(labelframe5)
        self.SqlEncodeE.configure(width=10)
        self.SqlEncodeE.pack(expand=False, fill="x", pady=1, side="top")
        self.SqlEncodeE.bind(
            "<<ComboboxSelected>>",
            self.sel_Sql_Encode,
            add="")
        labelframe5.pack(expand=True, fill="both", side="top")
        labelframe7 = ttk.Labelframe(frame13)
        labelframe7.configure(height=200, text='PVF数据', width=200)
        self.PVFCacheE = ttk.Combobox(labelframe7)
        self.PVFCacheE.configure(width=10)
        self.PVFCacheE.pack(expand=False, fill="x", pady=1, side="top")
        self.PVFCacheE.bind("<<ComboboxSelected>>", self.sel_PVF_Cache, add="")
        self.PVFEncodeE = ttk.Combobox(labelframe7)
        self.PVFEncodeE.configure(width=10)
        self.PVFEncodeE.pack(expand=False, fill="x", pady=1, side="top")
        self.openPVFBtn = ttk.Button(labelframe7)
        self.openPVFBtn.configure(text='读取PVF文件')
        self.openPVFBtn.pack(expand=False, fill="x", pady=1, side="top")
        self.openPVFBtn.configure(command=self.openPVF)
        labelframe7.pack(expand=True, fill="both", side="top")
        frame13.pack(fill="y", side="left")
        frame14 = ttk.Frame(self.searchFrame)
        frame14.configure(height=200, width=200)
        self.characTreeV = ttk.Treeview(frame14)
        self.characTreeV.configure(selectmode="browse", show="headings")
        self.characTreeV_cols = [
            'column1',
            'column2',
            'column3',
            'column4',
            'column5']
        self.characTreeV_dcols = [
            'column1',
            'column2',
            'column3',
            'column4',
            'column5']
        self.characTreeV.configure(
            columns=self.characTreeV_cols,
            displaycolumns=self.characTreeV_dcols)
        self.characTreeV.column(
            "column1",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.characTreeV.column(
            "column2",
            anchor="center",
            stretch=True,
            width=120,
            minwidth=20)
        self.characTreeV.column(
            "column3",
            anchor="center",
            stretch=True,
            width=40,
            minwidth=20)
        self.characTreeV.column(
            "column4",
            anchor="center",
            stretch=True,
            width=60,
            minwidth=20)
        self.characTreeV.column(
            "column5",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.characTreeV.heading("column1", anchor="center", text='角色ID')
        self.characTreeV.heading("column2", anchor="center", text='角色名')
        self.characTreeV.heading("column3", anchor="center", text='等级')
        self.characTreeV.heading("column4", anchor="center", text='职业')
        self.characTreeV.heading("column5", anchor="center", text='UID')
        self.characTreeV.pack(expand=True, fill="both", side="left")
        self.characTreeV.bind("<<TreeviewSelect>>", self.selectCharac, add="")
        self.characBar = ttk.Scrollbar(frame14)
        self.characBar.configure(orient="vertical")
        self.characBar.pack(fill="y", side="right")
        frame14.pack(expand=True, fill="both", side="left")
        self.searchFrame.pack(side="top")
        self.tabView.add(self.searchFrame, text='查询')
        self.pkgFrame = ttk.Frame(self.tabView)
        self.pkgFrame.configure(height=200, width=200)
        self.pkgTab = ttk.Notebook(self.pkgFrame)
        self.pkgTab.configure(height=200, width=200)
        self.invFrame = ttk.Frame(self.pkgTab)
        self.invFrame.configure(height=200, width=200)
        self.invFrame.pack(side="top")
        self.pkgTab.add(self.invFrame, text='物品栏')
        self.equFrame = ttk.Frame(self.pkgTab)
        self.equFrame.configure(height=200, width=200)
        self.equFrame.pack(side="top")
        self.pkgTab.add(self.equFrame, text='穿戴栏')
        self.creatureFrame = ttk.Frame(self.pkgTab)
        self.creatureFrame.configure(height=200, width=200)
        self.creatureFrame.pack(side="top")
        self.pkgTab.add(self.creatureFrame, text='宠物栏')
        self.cargoFrame = ttk.Frame(self.pkgTab)
        self.cargoFrame.configure(height=200, width=200)
        self.cargoFrame.pack(side="top")
        self.pkgTab.add(self.cargoFrame, text=' 仓库 ')
        self.accountCargoFrame = ttk.Frame(self.pkgTab)
        self.accountCargoFrame.configure(height=200, width=200)
        self.accountCargoFrame.pack(side="top")
        self.pkgTab.add(self.accountCargoFrame, text='账号金库')
        self.pkgTab.pack(expand=True, fill="both", side="top")
        self.pkgFrame.pack(side="top")
        self.tabView.add(self.pkgFrame, text=' 背包 ')
        self.mailF = ttk.Frame(self.tabView)
        self.mailF.configure(height=200, width=200)
        self.mailFrame = ttk.Frame(self.mailF)
        self.mailFrame.configure(height=200, width=200)
        self.mailFrame.pack(expand=True, fill="both", side="left")
        self.sendMailF = ttk.Labelframe(self.mailF)
        self.sendMailF.configure(height=200, text='发送邮件', width=150)
        frame6 = ttk.Frame(self.sendMailF)
        frame6.configure(height=200, width=200)
        self.itemBasicInfoFrame = ttk.Frame(frame6)
        self.itemBasicInfoFrame.configure(height=200, width=200)
        self.itemEditFrame = ttk.Frame(self.itemBasicInfoFrame)
        self.itemEditFrame.configure(height=200, width=200)
        self.itemSealBtn = ttk.Checkbutton(self.itemEditFrame)
        self.itemSealVar = tk.IntVar()
        self.itemSealBtn.configure(text='封装', variable=self.itemSealVar)
        self.itemSealBtn.grid(column=0, row=0)
        self.itemNameEntry = ttk.Combobox(self.itemEditFrame)
        self.itemNameEntry.configure(width=12)
        self.itemNameEntry.grid(column=1, columnspan=2, row=0, sticky="ew")
        self.itemIDEntry = ttk.Entry(self.itemEditFrame)
        self.itemIDEntry.configure(width=10)
        self.itemIDEntry.grid(column=1, columnspan=2, row=2, sticky="ew")
        self.numGradeLabel = ttk.Label(self.itemEditFrame)
        self.numGradeLabel.configure(text='数量：')
        self.numGradeLabel.grid(column=0, row=3)
        label17 = ttk.Label(self.itemEditFrame)
        label17.configure(text='增幅：')
        label17.grid(column=0, row=4)
        label18 = ttk.Label(self.itemEditFrame)
        label18.configure(text='强化：')
        label18.grid(column=0, row=5)
        label19 = ttk.Label(self.itemEditFrame)
        label19.configure(text='锻造：')
        label19.grid(column=0, row=6)
        self.numEntry = ttk.Spinbox(self.itemEditFrame)
        self.numEntry.configure(from_=0, to=999999999, width=16)
        self.numEntry.grid(column=1, row=3, sticky="nsew")
        label20 = ttk.Label(self.itemEditFrame)
        label20.configure(text='耐久：')
        label20.grid(column=2, padx=3, row=3, sticky="w")
        self.durabilityEntry = ttk.Spinbox(self.itemEditFrame)
        self.durabilityEntry.configure(from_=0, to=9999, width=6)
        self.durabilityEntry.grid(column=2, row=3, sticky="e")
        self.IncreaseTypeEntry = ttk.Combobox(self.itemEditFrame)
        self.IncreaseTypeEntry.configure(width=8)
        self.IncreaseTypeEntry.grid(column=1, row=4, sticky="ew")
        self.EnhanceEntry = ttk.Spinbox(self.itemEditFrame)
        self.EnhanceEntry.configure(from_=0, to=31, width=12)
        self.EnhanceEntry.grid(column=1, pady=0, row=5, sticky="nsew")
        self.forgingEntry = ttk.Spinbox(self.itemEditFrame)
        self.forgingEntry.configure(from_=0, to=999, width=12)
        self.forgingEntry.grid(column=1, pady=0, row=6, sticky="ew")
        self.IncreaseEntry = ttk.Spinbox(self.itemEditFrame)
        self.IncreaseEntry.configure(from_=0, to=99999, width=12)
        self.IncreaseEntry.grid(column=2, row=4, sticky="nsew")
        self.typeEntry = ttk.Combobox(self.itemEditFrame)
        self.typeEntry.configure(width=8)
        self.typeEntry.grid(column=2, row=5, sticky="ew")
        self.goldLabel = ttk.Label(self.itemEditFrame)
        self.goldLabel.configure(text='金币：')
        self.goldLabel.grid(column=2, padx=3, row=6, sticky="w")
        self.goldE = ttk.Spinbox(self.itemEditFrame)
        self.goldE.configure(from_=0, to=9999999999999999, width=6)
        self.goldE.grid(column=2, row=6, sticky="e")
        self.itemIDLabel = ttk.Label(self.itemEditFrame)
        self.itemIDLabel.configure(text='ID：')
        self.itemIDLabel.grid(column=0, row=2)
        self.itemEditFrame.grid(column=0, columnspan=3, row=0, sticky="nsew")
        self.itemEditFrame.columnconfigure("all", weight=1)
        label23 = ttk.Label(self.itemBasicInfoFrame)
        label23.configure(text='发件人：')
        label23.grid(column=0, pady=2, row=8)
        self.senderE = ttk.Combobox(self.itemBasicInfoFrame)
        self.senderE.configure(width=20)
        self.senderE.grid(column=1, columnspan=2, row=8, sticky="ew")
        label24 = ttk.Label(self.itemBasicInfoFrame)
        label24.configure(text='内容：')
        label24.grid(column=0, pady=2, row=9)
        self.msgE = ttk.Combobox(self.itemBasicInfoFrame)
        self.msgE.configure(width=12)
        self.msgE.grid(column=1, columnspan=2, row=9, sticky="ew")
        frame8 = ttk.Frame(self.itemBasicInfoFrame)
        frame8.configure(height=200, width=200)
        frame9 = ttk.Frame(frame8)
        frame9.configure(height=200, width=200)
        self.send2currentBtn = ttk.Button(frame9)
        self.send2currentBtn.configure(text='发送到当前角色')
        self.send2currentBtn.grid(column=0, row=0, sticky="ew")
        self.send2allBtn = ttk.Button(frame9)
        self.send2allBtn.configure(text='发送到全服角色')
        self.send2allBtn.grid(column=0, row=1, sticky="ew")
        self.send2VIPaBtn = ttk.Button(frame9)
        self.send2VIPaBtn.configure(text='发送到VIP账号')
        self.send2VIPaBtn.grid(column=0, row=2, sticky="ew")
        self.clearMailBtn = ttk.Button(frame9)
        self.clearMailBtn.configure(text='清空全服邮件')
        self.clearMailBtn.grid(column=1, row=0, sticky="ew")
        self.send2onlineBtn = ttk.Button(frame9)
        self.send2onlineBtn.configure(text='发送到在线角色')
        self.send2onlineBtn.grid(column=1, row=1, sticky="ew")
        self.send2VIPcBtn = ttk.Button(frame9)
        self.send2VIPcBtn.configure(text='发送到VIP角色')
        self.send2VIPcBtn.grid(column=1, row=2, sticky="ew")
        frame9.pack(expand=True, fill="x", side="top")
        frame9.columnconfigure("all", weight=1)
        frame8.grid(column=0, columnspan=3, row=10, sticky="nsew")
        separator6 = ttk.Separator(self.itemBasicInfoFrame)
        separator6.configure(orient="horizontal")
        separator6.grid(columnspan=3, pady=2, row=7, sticky="ew")
        self.itemBasicInfoFrame.pack(expand=True, fill="both", side="right")
        self.itemBasicInfoFrame.columnconfigure(0, pad=3)
        self.itemBasicInfoFrame.columnconfigure(1, weight=2)
        self.itemBasicInfoFrame.columnconfigure(2, weight=1)
        self.itemBasicInfoFrame.columnconfigure("all", pad=3)
        frame6.pack(expand=True, fill="both", side="left")
        self.sendMailF.pack(expand=False, fill="both", side="right")
        self.mailF.pack(side="top")
        self.tabView.add(self.mailF, text=' 邮件 ')
        self.creatureItemFrame = ttk.Frame(self.tabView)
        self.creatureItemFrame.configure(height=200, width=200)
        self.creatureItemFrame.pack(side="top")
        self.tabView.add(self.creatureItemFrame, text=' 宠物 ')
        self.avatarFrame = ttk.Frame(self.tabView)
        self.avatarFrame.configure(height=200, width=200)
        self.avatarFrame.pack(side="top")
        self.tabView.add(self.avatarFrame, text=' 时装 ')
        self.questFrame = ttk.Frame(self.tabView)
        self.questFrame.configure(height=200, width=200)
        self.questFrame.pack(side="top")
        self.tabView.add(self.questFrame, text=' 任务 ')
        self.gmToolFrame = ttk.Frame(self.tabView)
        self.gmToolFrame.configure(height=200, width=200)
        frame26 = ttk.Frame(self.gmToolFrame)
        frame26.configure(height=200, width=200)
        self.chargeFrame = ttk.Labelframe(frame26)
        self.chargeFrame.configure(height=200, text='充值', width=200)
        label26 = ttk.Label(self.chargeFrame)
        label26.configure(text='点券')
        label26.grid(column=0, row=0)
        label27 = ttk.Label(self.chargeFrame)
        label27.configure(text='代币')
        label27.grid(column=0, row=1)
        label28 = ttk.Label(self.chargeFrame)
        label28.configure(text='SP')
        label28.grid(column=0, row=2)
        label29 = ttk.Label(self.chargeFrame)
        label29.configure(text=' QP/TP ')
        label29.grid(column=0, row=3)
        entry1 = ttk.Entry(self.chargeFrame)
        self.ceraSVar = tk.StringVar()
        entry1.configure(state="readonly", textvariable=self.ceraSVar, width=8)
        entry1.grid(column=1, row=0, sticky="ew")
        entry2 = ttk.Entry(self.chargeFrame)
        self.ceraPointSVar = tk.StringVar()
        entry2.configure(
            state="readonly",
            textvariable=self.ceraPointSVar,
            width=8)
        entry2.grid(column=1, row=1, sticky="ew")
        entry3 = ttk.Entry(self.chargeFrame)
        self.spVar = tk.StringVar()
        entry3.configure(state="readonly", textvariable=self.spVar, width=8)
        entry3.grid(column=1, row=2, sticky="ew")
        entry4 = ttk.Entry(self.chargeFrame)
        self.qpTpVar = tk.StringVar()
        entry4.configure(state="readonly", textvariable=self.qpTpVar, width=8)
        entry4.grid(column=1, row=3, sticky="ew")
        self.ceraValueE = ttk.Spinbox(self.chargeFrame)
        self.ceraValueE.configure(from_=0, to=9999999999, width=12)
        self.ceraValueE.grid(column=2, row=0, sticky="ew")
        self.ceraTypeE = ttk.Combobox(self.chargeFrame)
        self.ceraTypeE.configure(
            state="readonly",
            values='点券 代币 SP TP QP',
            width=8)
        self.ceraTypeE.grid(column=2, row=1, sticky="ew")
        self.ceraChargeBtn = ttk.Button(self.chargeFrame)
        self.ceraChargeBtn.configure(text='充值')
        self.ceraChargeBtn.grid(column=2, row=2, sticky="ew")
        self.ceraClearBtn = ttk.Button(self.chargeFrame)
        self.ceraClearBtn.configure(text='清零')
        self.ceraClearBtn.grid(column=2, row=3, sticky="ew")
        self.chargeFrame.pack(expand=True, fill="both", side="left")
        self.chargeFrame.rowconfigure("all", weight=1)
        self.chargeFrame.columnconfigure("all", weight=1)
        self.PVPFrame = ttk.Labelframe(frame26)
        self.PVPFrame.configure(height=200, text='PVP', width=200)
        label5 = ttk.Label(self.PVPFrame)
        label5.configure(text='  段位  ')
        label5.grid(column=0, row=0)
        label30 = ttk.Label(self.PVPFrame)
        label30.configure(text='胜场')
        label30.grid(column=0, row=1)
        label7 = ttk.Label(self.PVPFrame)
        label7.configure(text='胜点')
        label7.grid(column=0, row=2)
        self.PVPwinNumE = ttk.Spinbox(self.PVPFrame)
        self.PVPwinNumE.configure(from_=0, to=9999999, width=12)
        self.PVPwinNumE.grid(column=1, row=1, sticky="ew")
        self.PVPgradeE = ttk.Combobox(self.PVPFrame)
        self.PVPgradeE.configure(
            state="readonly",
            values='点券 代币 SP TP QP',
            width=8)
        self.PVPgradeE.grid(column=1, row=0, sticky="ew")
        self.PVPCommitBtn = ttk.Button(self.PVPFrame)
        self.PVPCommitBtn.configure(text='提交')
        self.PVPCommitBtn.grid(column=0, columnspan=2, row=10, sticky="ew")
        self.PVPwinPointE = ttk.Spinbox(self.PVPFrame)
        self.PVPwinPointE.configure(from_=0, to=99999999, width=12)
        self.PVPwinPointE.grid(column=1, row=2, sticky="ew")
        self.PVPFrame.pack(expand=True, fill="both", side="left")
        self.PVPFrame.rowconfigure("all", weight=1)
        self.PVPFrame.columnconfigure("all", weight=1)
        self.labelframe3 = ttk.Labelframe(frame26)
        self.labelframe3.configure(height=200, text='其他功能', width=200)
        self.liftLimitBtn = ttk.Button(self.labelframe3)
        self.liftLimitBtn.configure(text='解除建号限制')
        self.liftLimitBtn.grid(column=0, row=0, sticky="ew")
        self.liftEquLevLimitBtn = ttk.Button(self.labelframe3)
        self.liftEquLevLimitBtn.configure(text='取消装备等级限制', width=12)
        self.liftEquLevLimitBtn.grid(column=0, row=1, sticky="ew")
        self.enableLRSlotBtn = ttk.Button(self.labelframe3)
        self.enableLRSlotBtn.configure(text='开启左右槽')
        self.enableLRSlotBtn.grid(column=0, row=2, sticky="ew")
        self.resetBloodDungeonBtn = ttk.Button(self.labelframe3)
        self.resetBloodDungeonBtn.configure(text='重置副本次数')
        self.resetBloodDungeonBtn.grid(column=1, row=0, sticky="ew")
        self.enableAllLevDungeonBtn = ttk.Button(self.labelframe3)
        self.enableAllLevDungeonBtn.configure(text='开启全图全难度', width=12)
        self.enableAllLevDungeonBtn.grid(column=1, row=1, sticky="ew")
        self.maxLevExpertBtn = ttk.Button(self.labelframe3)
        self.maxLevExpertBtn.configure(text='设置副职业满级')
        self.maxLevExpertBtn.grid(column=1, row=2, sticky="ew")
        self.labelframe3.pack(expand=True, fill="both", side="left")
        self.labelframe3.rowconfigure("all", weight=1)
        self.labelframe3.columnconfigure("all", weight=1)
        frame26.pack(fill="x", side="top")
        self.characInfoFrame = ttk.Frame(self.gmToolFrame)
        self.characInfoFrame.configure(height=200, width=200)
        self.characAndMoneyF = ttk.Frame(self.characInfoFrame)
        self.characAndMoneyF.configure(height=200, width=200)
        self.characInfoF = ttk.Labelframe(self.characAndMoneyF)
        self.characInfoF.configure(height=200, text='角色信息', width=200)
        self.characEntriesFrame = ttk.Frame(self.characInfoF)
        self.characEntriesFrame.configure(height=200, width=200)
        label12 = ttk.Label(self.characEntriesFrame)
        label12.configure(text='角色名：')
        label12.grid(column=0, row=0)
        self.nameE = ttk.Entry(self.characEntriesFrame)
        self.nameE.configure(width=20)
        self.nameE.grid(
            column=1,
            columnspan=2,
            padx=1,
            pady=1,
            row=0,
            sticky="ew")
        label13 = ttk.Label(self.characEntriesFrame)
        label13.configure(text='角色等级：')
        label13.grid(column=0, row=1)
        self.levE = ttk.Spinbox(self.characEntriesFrame)
        self.levE.configure(from_=1, to=999, width=10)
        self.levE.grid(column=1, padx=1, pady=1, row=1, sticky="ew")
        checkbutton2 = ttk.Checkbutton(self.characEntriesFrame)
        self.isVIP = tk.IntVar()
        checkbutton2.configure(text='VIP账户', variable=self.isVIP)
        checkbutton2.grid(column=2, row=1)
        label14 = ttk.Label(self.characEntriesFrame)
        label14.configure(text='职业：')
        label14.grid(column=0, row=2)
        self.jobE = ttk.Combobox(self.characEntriesFrame)
        self.jobE.configure(width=8)
        self.jobE.grid(column=1, padx=1, pady=1, row=2, sticky="ew")
        self.jobE2 = ttk.Combobox(self.characEntriesFrame)
        self.jobE2.configure(width=8)
        self.jobE2.grid(column=2, padx=1, row=2, sticky="ew")
        label15 = ttk.Label(self.characEntriesFrame)
        label15.configure(text='成长类型：')
        label15.grid(column=0, row=3)
        self.growTypeE = ttk.Combobox(self.characEntriesFrame)
        self.growTypeE.configure(width=8)
        self.growTypeE.grid(
            column=1,
            columnspan=1,
            padx=1,
            pady=1,
            row=3,
            sticky="ew")
        label16 = ttk.Label(self.characEntriesFrame)
        label16.configure(text='觉醒标识：')
        label16.grid(column=0, row=4)
        self.wakeFlgE = ttk.Combobox(self.characEntriesFrame)
        self.wakeFlgE.configure(width=8)
        self.wakeFlgE.grid(column=1, padx=1, pady=1, row=4, sticky="ew")
        checkbutton3 = ttk.Checkbutton(self.characEntriesFrame)
        self.isReturnUser = tk.IntVar()
        checkbutton3.configure(text='回归玩家', variable=self.isReturnUser)
        checkbutton3.grid(column=2, row=3)
        self.commitBtn = ttk.Button(self.characEntriesFrame)
        self.commitBtn.configure(text='提交修改')
        self.commitBtn.grid(column=0, columnspan=3, padx=1, row=5, sticky="ew")
        self.cInfoSetBanedBtn = ttk.Checkbutton(self.characEntriesFrame)
        self.isBanedUser = tk.IntVar()
        self.cInfoSetBanedBtn.configure(text='封停账号', variable=self.isBanedUser)
        self.cInfoSetBanedBtn.grid(column=2, row=4)
        self.characEntriesFrame.pack(
            anchor="center",
            expand=False,
            fill="x",
            padx=5,
            pady=5,
            side="top")
        self.characEntriesFrame.rowconfigure("all", weight=1)
        self.characEntriesFrame.columnconfigure(1, weight=1)
        self.characInfoF.pack(expand=True, fill="both", side="top")
        self.moneyF = ttk.Labelframe(self.characAndMoneyF)
        self.moneyF.configure(height=200, text='金币复活币', width=200)
        self.pkgMoneyE = ttk.Spinbox(self.moneyF)
        self.pkgMoneyE.configure(from_=0, to=999999999999, width=15)
        self.pkgMoneyE.grid(column=1, row=0, sticky="ew")
        self.pkgMoneyBtn = ttk.Button(self.moneyF)
        self.pkgMoneyBtn.configure(text='提交修改')
        self.pkgMoneyBtn.grid(column=2, row=0, sticky="ew")
        self.accountMoneyE = ttk.Spinbox(self.moneyF)
        self.accountMoneyE.configure(from_=0, to=999999999999, width=15)
        self.accountMoneyE.grid(column=1, row=1, sticky="ew")
        self.accountMoneyBtn = ttk.Button(self.moneyF)
        self.accountMoneyBtn.configure(text='提交修改')
        self.accountMoneyBtn.grid(column=2, row=1, sticky="ew")
        label8 = ttk.Label(self.moneyF)
        label8.configure(text=' 背包 ')
        label8.grid(column=0, row=0)
        label9 = ttk.Label(self.moneyF)
        label9.configure(text=' 金库 ')
        label9.grid(column=0, row=1)
        self.payCoinE = ttk.Spinbox(self.moneyF)
        self.payCoinE.configure(from_=0, to=999999999999, width=15)
        self.payCoinE.grid(column=1, row=2, sticky="ew")
        self.payCoinBtn = ttk.Button(self.moneyF)
        self.payCoinBtn.configure(text='提交修改')
        self.payCoinBtn.grid(column=2, row=2, sticky="ew")
        label10 = ttk.Label(self.moneyF)
        label10.configure(text='复活币')
        label10.grid(column=0, row=2)
        self.moneyF.pack(expand=True, fill="both", side="top")
        self.moneyF.columnconfigure("all", weight=1)
        self.characAndMoneyF.pack(expand=False, fill="both", side="left")
        self.bubbleEventF = ttk.Frame(self.characInfoFrame)
        self.bubbleEventF.configure(height=200, width=200)
        notebook1 = ttk.Notebook(self.bubbleEventF)
        notebook1.configure(height=200, width=200)
        frame22 = ttk.Frame(notebook1)
        frame22.configure(height=200, width=200)
        frame25 = ttk.Frame(frame22)
        frame25.configure(height=200, width=200)
        labelframe6 = ttk.Labelframe(frame25)
        labelframe6.configure(height=200, text='普通泡点', width=200)
        self.enableBubbleBtn1 = ttk.Checkbutton(labelframe6)
        self.enableBubbleVar = tk.IntVar()
        self.enableBubbleBtn1.configure(
            text='启用泡点', variable=self.enableBubbleVar)
        self.enableBubbleBtn1.grid(column=0, columnspan=1, row=4, sticky="ew")
        label22 = ttk.Label(labelframe6)
        label22.configure(text='分钟间隔：')
        label22.grid(column=0, row=1)
        self.bubbleIntervalE1 = ttk.Combobox(labelframe6)
        self.bubbleIntervalE1.configure(
            values='1 2 3 4 5 10 15 20 30', width=15)
        self.bubbleIntervalE1.grid(column=1, row=1, sticky="ew")
        label25 = ttk.Label(labelframe6)
        label25.configure(text='发放数额：')
        label25.grid(column=0, row=2)
        self.bubbleValueE1 = ttk.Combobox(labelframe6)
        self.bubbleValueE1.configure(values='1 5 10 20 50 100', width=15)
        self.bubbleValueE1.grid(column=1, row=2, sticky="ew")
        self.timeLabel1 = ttk.Label(labelframe6)
        self.timeLabel1.configure(text='有效时间：')
        self.timeLabel1.grid(column=0, row=3)
        self.timeF1 = ttk.Frame(labelframe6)
        self.timeF1.configure(height=200, width=200)
        self.startHourE = ttk.Spinbox(self.timeF1)
        self.startHourE.configure(from_=0, to=23, width=2)
        self.startHourE.pack(expand=True, fill="x", side="left")
        self.startMinE = ttk.Spinbox(self.timeF1)
        self.startMinE.configure(from_=0, to=59, width=2)
        self.startMinE.pack(expand=True, fill="x", side="left")
        label38 = ttk.Label(self.timeF1)
        label38.configure(text='-')
        label38.pack(side="left")
        self.stopHourE = ttk.Spinbox(self.timeF1)
        self.stopHourE.configure(from_=0, to=23, width=2)
        self.stopHourE.pack(expand=True, fill="x", side="left")
        self.stopMinE = ttk.Spinbox(self.timeF1)
        self.stopMinE.configure(from_=0, to=59, width=2)
        self.stopMinE.pack(expand=True, fill="x", side="left")
        self.timeF1.grid(column=1, row=3, sticky="ew")
        self.saveBubbleBtn1 = ttk.Button(labelframe6)
        self.saveBubbleBtn1.configure(text='保存泡点')
        self.saveBubbleBtn1.grid(column=1, row=4, sticky="ew")
        labelframe6.pack(expand=True, fill="both", side="top")
        labelframe6.columnconfigure("all", weight=1)
        self.accountBubbleF = ttk.Labelframe(frame25)
        self.accountBubbleF.configure(height=200, text='账号泡点', width=200)
        self.enableBubbleBtn2 = ttk.Checkbutton(self.accountBubbleF)
        self.enableBubbleVar2 = tk.IntVar()
        self.enableBubbleBtn2.configure(
            text='启用泡点', variable=self.enableBubbleVar2)
        self.enableBubbleBtn2.grid(column=0, columnspan=1, row=4, sticky="ew")
        label39 = ttk.Label(self.accountBubbleF)
        label39.configure(text='分钟间隔：')
        label39.grid(column=0, row=1)
        self.bubbleIntervalE2 = ttk.Combobox(self.accountBubbleF)
        self.bubbleIntervalE2.configure(
            values='1 2 3 4 5 10 15 20 30', width=15)
        self.bubbleIntervalE2.grid(column=1, row=1, sticky="ew")
        label40 = ttk.Label(self.accountBubbleF)
        label40.configure(text='发放数额：')
        label40.grid(column=0, row=2)
        self.bubbleValueE2 = ttk.Combobox(self.accountBubbleF)
        self.bubbleValueE2.configure(values='1 5 10 20 50 100', width=15)
        self.bubbleValueE2.grid(column=1, row=2, sticky="ew")
        self.timeLabel2 = ttk.Label(self.accountBubbleF)
        self.timeLabel2.configure(text='有效时间：')
        self.timeLabel2.grid(column=0, row=3)
        self.timeF2 = ttk.Frame(self.accountBubbleF)
        self.timeF2.configure(height=200, width=200)
        self.startHourE2 = ttk.Spinbox(self.timeF2)
        self.startHourE2.configure(from_=0, to=23, width=2)
        self.startHourE2.pack(expand=True, fill="x", side="left")
        self.startMinE2 = ttk.Spinbox(self.timeF2)
        self.startMinE2.configure(from_=0, to=59, width=2)
        self.startMinE2.pack(expand=True, fill="x", side="left")
        label42 = ttk.Label(self.timeF2)
        label42.configure(text='-')
        label42.pack(side="left")
        self.stopHourE2 = ttk.Spinbox(self.timeF2)
        self.stopHourE2.configure(from_=0, to=23, width=2)
        self.stopHourE2.pack(expand=True, fill="x", side="left")
        self.stopMinE2 = ttk.Spinbox(self.timeF2)
        self.stopMinE2.configure(from_=0, to=59, width=2)
        self.stopMinE2.pack(expand=True, fill="x", side="left")
        self.timeF2.grid(column=1, row=3, sticky="ew")
        self.saveBubbleBtn2 = ttk.Button(self.accountBubbleF)
        self.saveBubbleBtn2.configure(text='保存泡点')
        self.saveBubbleBtn2.grid(column=1, row=4, sticky="ew")
        label43 = ttk.Label(self.accountBubbleF)
        label43.configure(text='泡点编号：')
        label43.grid(column=0, row=0)
        self.bubbleIDE = ttk.Combobox(self.accountBubbleF)
        self.bubbleIDE.configure(state="readonly", width=15)
        self.bubbleIDE.grid(column=1, row=0, sticky="ew")
        self.accountBubbleF.pack(expand=True, fill="both", side="top")
        self.accountBubbleF.columnconfigure("all", weight=1)
        frame25.pack(fill="y", side="left")
        self.bubbleAccountF = ttk.Labelframe(frame22)
        self.bubbleAccountF.configure(height=200, text='账号列表', width=200)
        frame30 = ttk.Frame(self.bubbleAccountF)
        frame30.configure(height=200, width=200)
        checkbutton5 = ttk.Checkbutton(frame30)
        self.privateIPVar = tk.IntVar()
        checkbutton5.configure(text='对假人发放泡点', variable=self.privateIPVar)
        checkbutton5.pack(anchor="e", side="right")
        label44 = ttk.Label(frame30)
        label44.configure(foreground="#408080", text='[提示]该列表仅针对于账号泡点')
        label44.pack(padx=5, side="left")
        frame30.pack(fill="x", side="top")
        frame28 = ttk.Frame(self.bubbleAccountF)
        frame28.configure(height=200, width=200)
        self.bubbleAccountTree = ttk.Treeview(frame28)
        self.bubbleAccountTree.configure(
            height=8, selectmode="extended", show="headings")
        self.bubbleAccountTree_cols = ['column9', 'column19']
        self.bubbleAccountTree_dcols = ['column9', 'column19']
        self.bubbleAccountTree.configure(
            columns=self.bubbleAccountTree_cols,
            displaycolumns=self.bubbleAccountTree_dcols)
        self.bubbleAccountTree.column(
            "column9",
            anchor="center",
            stretch=True,
            width=40,
            minwidth=20)
        self.bubbleAccountTree.column(
            "column19",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.bubbleAccountTree.heading("column9", anchor="center", text='UID')
        self.bubbleAccountTree.heading("column19", anchor="center", text='状态')
        self.bubbleAccountTree.pack(expand=True, fill="both", side="left")
        self.bubbleAccountBar = ttk.Scrollbar(frame28)
        self.bubbleAccountBar.configure(orient="vertical")
        self.bubbleAccountBar.pack(fill="y", side="right")
        frame28.pack(expand=True, fill="both", side="top")
        frame29 = ttk.Frame(self.bubbleAccountF)
        frame29.configure(height=200, width=200)
        self.bubbleUIDE = ttk.Entry(frame29)
        self.bubbleUIDE.configure(width=10)
        self.bubbleUIDE.pack(expand=True, fill="both", side="left")
        self.addBubbleUIDBtn = ttk.Button(frame29)
        self.addBubbleUIDBtn.configure(text='添加账号')
        self.addBubbleUIDBtn.pack(expand=False, fill="x", side="left")
        self.rmBubbleUIDBtn = ttk.Button(frame29)
        self.rmBubbleUIDBtn.configure(text='移除选中')
        self.rmBubbleUIDBtn.pack(expand=False, fill="x", side="left")
        frame29.pack(fill="x", side="top")
        self.bubbleAccountF.pack(expand=True, fill="both", side="right")
        frame22.pack(side="top")
        notebook1.add(frame22, text='在线泡点')
        frame23 = ttk.Frame(notebook1)
        frame23.configure(height=200, width=200)
        self.eventTreeNow = ttk.Treeview(frame23)
        self.eventTreeNow.configure(
            height=6, selectmode="extended", show="headings")
        self.eventTreeNow_cols = [
            'column25', 'column29', 'column38', 'column39']
        self.eventTreeNow_dcols = ['column25', 'column29', 'column38']
        self.eventTreeNow.configure(
            columns=self.eventTreeNow_cols,
            displaycolumns=self.eventTreeNow_dcols)
        self.eventTreeNow.column(
            "column25",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.eventTreeNow.column(
            "column29",
            anchor="center",
            stretch=True,
            width=100,
            minwidth=20)
        self.eventTreeNow.column(
            "column38",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.eventTreeNow.column(
            "column39",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.eventTreeNow.heading("column25", anchor="center", text='活动ID')
        self.eventTreeNow.heading("column29", anchor="center", text='活动描述')
        self.eventTreeNow.heading("column38", anchor="center", text='参数')
        self.eventTreeNow.heading("column39", anchor="center", text='参数2')
        self.eventTreeNow.pack(expand=True, fill="both", side="top")
        frame18 = ttk.Frame(frame23)
        frame18.configure(height=200, width=200)
        self.refreshEventBtn = ttk.Button(frame18)
        self.refreshEventBtn.configure(text='刷新活动')
        self.refreshEventBtn.pack(expand=True, fill="x", side="left")
        self.delEventBtn = ttk.Button(frame18)
        self.delEventBtn.configure(text='删除活动')
        self.delEventBtn.pack(expand=True, fill="x", side="right")
        frame18.pack(fill="x", side="top")
        frame15 = ttk.Frame(frame23)
        frame15.configure(height=200, width=200)
        label36 = ttk.Label(frame15)
        label36.configure(foreground="#0080ff", text='活动名称')
        label36.grid(column=0, row=0)
        self.eventNameE = ttk.Combobox(frame15)
        self.eventNameE.configure(width=12)
        self.eventNameE.grid(column=0, row=1, sticky="ew")
        label37 = ttk.Label(frame15)
        label37.configure(foreground="#0080ff", text='参数')
        label37.grid(column=1, row=0)
        self.eventArg1E = ttk.Entry(frame15)
        self.eventArg1E.configure(width=8)
        self.eventArg1E.grid(column=1, row=1, sticky="ew")
        self.addEventBtn = ttk.Button(frame15)
        self.addEventBtn.configure(text='添加活动')
        self.addEventBtn.grid(column=2, row=1, rowspan=1, sticky="ew")
        frame15.pack(fill="x", side="top")
        frame15.columnconfigure("all", weight=1)
        frame23.pack(side="top")
        notebook1.add(frame23, text='活动管理')
        notebook1.pack(expand=True, fill="both", side="top")
        self.bubbleEventF.pack(expand=True, fill="both", side="left")
        self.characInfoFrame.pack(expand=True, fill="both", side="top")
        self.gmToolFrame.pack(expand=True, fill="both", side="top")
        self.tabView.add(self.gmToolFrame, text=' GM ')
        frame5 = ttk.Frame(self.tabView)
        frame5.configure(height=200, width=200)
        frame17 = ttk.Frame(frame5)
        frame17.configure(height=200, width=200)
        self.banedTreeV = ttk.Treeview(frame17)
        self.banedTreeV.configure(
            height=10,
            selectmode="extended",
            show="headings")
        self.banedTreeV_cols = [
            'column23',
            'column14',
            'column15',
            'column16',
            'column17',
            'column18',
            'column24',
            'column6']
        self.banedTreeV_dcols = [
            'column23',
            'column14',
            'column15',
            'column16',
            'column17',
            'column18',
            'column24',
            'column6']
        self.banedTreeV.configure(
            columns=self.banedTreeV_cols,
            displaycolumns=self.banedTreeV_dcols)
        self.banedTreeV.column(
            "column23",
            anchor="center",
            stretch=True,
            width=40,
            minwidth=20)
        self.banedTreeV.column(
            "column14",
            anchor="center",
            stretch=True,
            width=40,
            minwidth=20)
        self.banedTreeV.column(
            "column15",
            anchor="center",
            stretch=True,
            width=40,
            minwidth=20)
        self.banedTreeV.column(
            "column16",
            anchor="center",
            stretch=True,
            width=20,
            minwidth=20)
        self.banedTreeV.column(
            "column17",
            anchor="center",
            stretch=True,
            width=60,
            minwidth=20)
        self.banedTreeV.column(
            "column18",
            anchor="center",
            stretch=True,
            width=30,
            minwidth=20)
        self.banedTreeV.column(
            "column24",
            anchor="center",
            stretch=True,
            width=50,
            minwidth=20)
        self.banedTreeV.column(
            "column6",
            anchor="center",
            stretch=True,
            width=25,
            minwidth=20)
        self.banedTreeV.heading("column23", anchor="center", text='账号')
        self.banedTreeV.heading("column14", anchor="center", text='UID')
        self.banedTreeV.heading("column15", anchor="center", text='角色ID')
        self.banedTreeV.heading("column16", anchor="center", text='等级')
        self.banedTreeV.heading("column17", anchor="center", text='角色名')
        self.banedTreeV.heading("column18", anchor="center", text='职业')
        self.banedTreeV.heading("column24", anchor="center", text='IP')
        self.banedTreeV.heading("column6", anchor="center", text='类型')
        self.banedTreeV.pack(expand=True, fill="both", side="left")
        self.banedBar = ttk.Scrollbar(frame17)
        self.banedBar.configure(orient="vertical")
        self.banedBar.pack(fill="y", side="right")
        frame17.pack(expand=True, fill="both", side="top")
        frame16 = ttk.Frame(frame5)
        frame16.configure(height=200, width=200)
        self.resumeBanedBtn = ttk.Button(frame16)
        self.resumeBanedBtn.configure(text='解除选中封停')
        self.resumeBanedBtn.pack(expand=True, fill="x", side="left")
        self.punishTypeE = ttk.Combobox(frame16)
        self.punishTypeE.configure(values='禁止登陆 限制交易', width=8)
        self.punishTypeE.pack(padx=5, side="left")
        label11 = ttk.Label(frame16)
        label11.configure(text='账号ID：')
        label11.pack(side="left")
        self.banAnameE = ttk.Entry(frame16)
        self.banAnameE.configure(width=15)
        self.banAnameE.pack(side="left")
        self.setBanedABtn = ttk.Button(frame16)
        self.setBanedABtn.configure(text='封禁')
        self.setBanedABtn.pack(expand=True, fill="x", side="left")
        label21 = ttk.Label(frame16)
        label21.configure(text='  角色名：')
        label21.pack(side="left")
        self.banCnameE = ttk.Entry(frame16)
        self.banCnameE.configure(width=15)
        self.banCnameE.pack(side="left")
        self.setBanedCBtn = ttk.Button(frame16)
        self.setBanedCBtn.configure(text='封禁')
        self.setBanedCBtn.pack(expand=True, fill="x", side="left")
        frame16.pack(fill="x", side="top")
        frame5.pack(side="top")
        self.tabView.add(frame5, text=' 封停 ')
        self.characMainFrame = ttk.Frame(self.tabView)
        self.characMainFrame.configure(height=200, width=200)
        frame3 = ttk.Frame(self.characMainFrame)
        frame3.configure(height=200, width=200)
        self.otherFunctionFrame = ttk.Labelframe(frame3)
        self.otherFunctionFrame.configure(height=200, text='附加功能', width=160)
        frame7 = ttk.Frame(self.otherFunctionFrame)
        frame7.configure(height=100, width=150)
        self.saveStartBtn = ttk.Button(frame7)
        self.saveStartBtn.configure(text='生成一键启动器')
        self.saveStartBtn.pack(fill="x", pady=1, side="top")
        self.pvfCacheMBtn = ttk.Button(frame7)
        self.pvfCacheMBtn.configure(text='PVF缓存管理器')
        self.pvfCacheMBtn.pack(fill="x", pady=1, side="top")
        self.pvfCacheMBtn.configure(command=self.open_PVF_Cache_Edit)
        self.pvfToolBtn = ttk.Button(frame7)
        self.pvfToolBtn.configure(text='PVF工具')
        self.pvfToolBtn.pack(fill="x", pady=1, side="top")
        self.pvfToolBtn.configure(command=self._open_PVF_Editor)
        self.enableAuctionBtn = ttk.Button(frame7)
        self.enableAuctionBtn.configure(text='启用拍卖行')
        self.enableAuctionBtn.pack(fill="x", pady=1, side="top")
        self.saveResolutionBtn = ttk.Button(frame7)
        self.saveResolutionBtn.configure(text='保存当前分辨率')
        self.saveResolutionBtn.pack(fill="x", pady=1, side="top")
        self.saveResolutionBtn.configure(command=self.save_resolution)
        self.checkUpdateBtn = ttk.Checkbutton(frame7)
        self.updateCheckVar = tk.IntVar()
        self.checkUpdateBtn.configure(
            text='自动检查更新', variable=self.updateCheckVar)
        self.checkUpdateBtn.pack(expand=True, side="top")
        self.HDresolutionBtn = ttk.Checkbutton(frame7)
        self.HDResolutionVar = tk.IntVar()
        self.HDresolutionBtn.configure(
            text='高分辨率缩放', variable=self.HDResolutionVar)
        self.HDresolutionBtn.pack(expand=True, side="top")
        self.checkbutton1 = ttk.Checkbutton(frame7)
        self.onlineNumVar = tk.IntVar()
        self.checkbutton1.configure(text='在线人数更新', variable=self.onlineNumVar)
        self.checkbutton1.pack(expand=True, side="top")
        self.themeE = ttk.Combobox(frame7)
        self.themeE.configure(width=8)
        self.themeE.pack(expand=True, fill="x", side="top")
        self.themeE.bind("<<ComboboxSelected>>", self.change_Theme, add="")
        frame7.pack(expand=True, fill="both", padx=3, side="top")
        self.otherFunctionFrame.pack(fill="y", side="left")
        self.gitHubFrame = ttk.Frame(frame3)
        self.gitHubFrame.configure(height=160, width=160)
        self.gitHubFrame.pack(side="right")
        frame34 = ttk.Frame(frame3)
        frame34.configure(height=200, width=200)
        labelframe10 = ttk.Labelframe(frame34)
        labelframe10.configure(height=200, text='服务器管理', width=200)
        frame35 = ttk.Frame(labelframe10)
        frame35.configure(height=200, width=200)
        frame10 = ttk.Frame(frame35)
        frame10.configure(height=200, width=200)
        frame11 = ttk.Frame(frame10)
        frame11.configure(height=200, width=200)
        label32 = ttk.Label(frame11)
        label32.configure(text='服务器IP')
        label32.pack(side="left")
        self.ipE2 = ttk.Entry(frame11)
        self.ipE2.configure(width=15)
        self.ipE2.pack(expand=False, fill="x", side="left")
        label33 = ttk.Label(frame11)
        label33.configure(text='端口')
        label33.pack(side="left")
        self.portE2 = ttk.Entry(frame11)
        self.portE2.configure(width=4)
        self.portE2.pack(side="left")
        label34 = ttk.Label(frame11)
        label34.configure(text='用户名')
        label34.pack(side="left")
        self.userE2 = ttk.Entry(frame11)
        self.userE2.configure(width=6)
        self.userE2.pack(side="left")
        label35 = ttk.Label(frame11)
        label35.configure(text='密码')
        label35.pack(side="left")
        self.pwdE2 = ttk.Entry(frame11)
        self.pwdE2.configure(width=10)
        self.pwdE2.pack(expand=True, fill="x", side="top")
        frame11.pack(fill="x", side="top")
        frame12 = ttk.Frame(frame10)
        frame12.configure(height=200, width=200)
        self.sshConBtn = ttk.Button(frame12)
        self.sshConBtn.configure(text='连接服务器', width=8)
        self.sshConBtn.pack(expand=True, fill="x", side="left")
        self.SSHKeyConBtn = ttk.Button(frame12)
        self.SSHKeyConBtn.configure(text='密钥连接', width=8)
        self.SSHKeyConBtn.pack(expand=True, fill="x", side="left")
        self.runServerBtn = ttk.Button(frame12)
        self.runServerBtn.configure(text='启动服务器', width=8)
        self.runServerBtn.pack(expand=True, fill="x", side="left")
        self.stopServerBtn = ttk.Button(frame12)
        self.stopServerBtn.configure(text='停止服务器', width=8)
        self.stopServerBtn.pack(expand=True, fill="x", side="left")
        self.restartChBtn = ttk.Button(frame12)
        self.restartChBtn.configure(text='重启频道', width=8)
        self.restartChBtn.pack(expand=True, fill="x", side="left")
        self.uploadPVFBtn = ttk.Button(frame12)
        self.uploadPVFBtn.configure(text='上传PVF', width=8)
        self.uploadPVFBtn.pack(expand=True, fill="x", side="left")
        frame12.pack(expand=True, fill="both", side="top")
        frame10.pack(fill="x", side="top")
        self.SSHDIYFrame = ttk.Labelframe(frame35)
        self.SSHDIYFrame.configure(height=200, text='自定义指令', width=200)
        frame20 = ttk.Frame(self.SSHDIYFrame)
        frame20.configure(height=200, width=200)
        self.cmdE1 = ttk.Combobox(frame20)
        self.cmdE1.grid(column=0, row=0)
        self.cmdE2 = ttk.Combobox(frame20)
        self.cmdE2.grid(column=0, row=1)
        self.cmdE3 = ttk.Combobox(frame20)
        self.cmdE3.grid(column=0, row=2)
        self.cmdE4 = ttk.Combobox(frame20)
        self.cmdE4.grid(column=0, row=3)
        self.runBtn1 = ttk.Button(frame20)
        self.runBtn1.configure(text='执行')
        self.runBtn1.grid(column=1, row=0)
        self.runBtn2 = ttk.Button(frame20)
        self.runBtn2.configure(text='执行')
        self.runBtn2.grid(column=1, row=1)
        self.runBtn3 = ttk.Button(frame20)
        self.runBtn3.configure(text='执行')
        self.runBtn3.grid(column=1, row=2)
        self.runBtn4 = ttk.Button(frame20)
        self.runBtn4.configure(text='执行')
        self.runBtn4.grid(column=1, row=3)
        frame20.pack(side="left")
        frame21 = ttk.Frame(self.SSHDIYFrame)
        frame21.configure(height=200, width=200)
        self.shellLogE = tk.Text(frame21)
        self.shellLogE.configure(height=5, width=50)
        self.shellLogE.pack(expand=True, fill="both", side="top")
        frame21.pack(expand=True, fill="both", side="top")
        self.SSHDIYFrame.pack(expand=True, fill="both", side="top")
        frame35.pack(expand=True, fill="both", side="top")
        labelframe10.pack(expand=True, fill="both", side="top")
        frame34.pack(expand=True, fill="both", side="left")
        frame3.pack(fill="x", side="top")
        self.imageFrame = ttk.Frame(self.characMainFrame)
        self.imageFrame.configure(height=200, width=200)
        self.imageFrame.pack(expand=True, fill="both", side="top")
        self.characMainFrame.pack(side="top")
        self.tabView.add(self.characMainFrame, text=' 其它 ')
        frame38 = ttk.Frame(self.tabView)
        frame38.configure(height=200, width=200)
        notebook2 = ttk.Notebook(frame38)
        notebook2.configure(height=200, width=200)
        frame36 = ttk.Frame(notebook2)
        frame36.configure(height=200, width=200)
        labelframe2 = ttk.Labelframe(frame36)
        labelframe2.configure(height=200, text='数据库备份', width=200)
        self.remoteSqlTree = ttk.Treeview(labelframe2)
        self.remoteSqlTree.configure(
            height=6, selectmode="extended", show="headings")
        self.remoteSqlTree_cols = ['column7', 'column8']
        self.remoteSqlTree_dcols = ['column7', 'column8']
        self.remoteSqlTree.configure(
            columns=self.remoteSqlTree_cols,
            displaycolumns=self.remoteSqlTree_dcols)
        self.remoteSqlTree.column(
            "column7",
            anchor="w",
            stretch=True,
            width=100,
            minwidth=20)
        self.remoteSqlTree.column(
            "column8",
            anchor="w",
            stretch=True,
            width=50,
            minwidth=20)
        self.remoteSqlTree.heading("column7", anchor="w", text='数据库')
        self.remoteSqlTree.heading("column8", anchor="w", text='状态')
        self.remoteSqlTree.pack(expand=True, fill="both", side="top")
        frame39 = ttk.Frame(labelframe2)
        frame39.configure(height=200, width=200)
        button2 = ttk.Button(frame39)
        button2.configure(text='备份选中数据库', width=15)
        button2.pack(expand=True, fill="x", side="right")
        button2.configure(command=self.backup_sel_db)
        button6 = ttk.Button(frame39)
        button6.configure(text='全选', width=15)
        button6.pack(expand=True, fill="x", side="left")
        button6.configure(command=self.sel_all_remote_db)
        frame39.pack(fill="x", side="top")
        labelframe2.pack(expand=True, fill="both", side="left")
        labelframe9 = ttk.Labelframe(frame36)
        labelframe9.configure(height=200, text='数据库还原', width=200)
        self.localSqlTree = ttk.Treeview(labelframe9)
        self.localSqlTree.configure(
            height=5, selectmode="extended", show="headings")
        self.localSqlTree_cols = ['column10', 'column11']
        self.localSqlTree_dcols = ['column10', 'column11']
        self.localSqlTree.configure(
            columns=self.localSqlTree_cols,
            displaycolumns=self.localSqlTree_dcols)
        self.localSqlTree.column(
            "column10",
            anchor="w",
            stretch=True,
            width=100,
            minwidth=20)
        self.localSqlTree.column(
            "column11",
            anchor="w",
            stretch=True,
            width=50,
            minwidth=20)
        self.localSqlTree.heading("column10", anchor="w", text='数据库')
        self.localSqlTree.heading("column11", anchor="w", text='状态')
        self.localSqlTree.pack(expand=True, fill="both", side="top")
        frame37 = ttk.Frame(labelframe9)
        frame37.configure(height=200, width=200)
        button4 = ttk.Button(frame37)
        button4.configure(text='打开文件夹', width=15)
        button4.pack(expand=True, fill="x", side="left")
        button4.configure(command=self.open_db_bak_dir)
        button3 = ttk.Button(frame37)
        button3.configure(text='恢复选中数据库', width=15)
        button3.pack(expand=True, fill="x", side="left")
        button3.configure(command=self.restore_sel_db)
        frame37.pack(fill="x", side="top")
        labelframe9.pack(expand=True, fill="both", side="left")
        labelframe11 = ttk.Labelframe(frame36)
        labelframe11.configure(height=200, text='数据库爆破', width=200)
        button5 = ttk.Button(labelframe11)
        button5.configure(text='数据库重置', width=20)
        button5.pack(expand=True, side="top")
        button5.configure(command=self.init_db)
        label41 = ttk.Label(labelframe11)
        label41.configure(foreground="#ff0000", text='此功能将清空所有数据')
        label41.pack(expand=True, side="top")
        label49 = ttk.Label(labelframe11)
        label49.configure(foreground="#ff8040", text='此功能将清空所有数据')
        label49.pack(expand=True, side="top")
        label50 = ttk.Label(labelframe11)
        label50.configure(foreground="#ffff00", text='此功能将清空所有数据')
        label50.pack(expand=True, side="top")
        label51 = ttk.Label(labelframe11)
        label51.configure(foreground="#00ff00", text='此功能将清空所有数据')
        label51.pack(expand=True, side="top")
        label52 = ttk.Label(labelframe11)
        label52.configure(foreground="#00ffff", text='此功能将清空所有数据')
        label52.pack(expand=True, side="top")
        label53 = ttk.Label(labelframe11)
        label53.configure(foreground="#0000ff", text='此功能将清空所有数据')
        label53.pack(expand=True, side="top")
        label54 = ttk.Label(labelframe11)
        label54.configure(foreground="#8000ff", text='此功能将清空所有数据')
        label54.pack(expand=True, side="top")
        label55 = ttk.Label(labelframe11)
        label55.configure(foreground="#ff00ff", text='此功能将清空所有数据')
        label55.pack(expand=True, side="top")
        label56 = ttk.Label(labelframe11)
        label56.configure(foreground="#ff0000", text='此功能将清空所有数据')
        label56.pack(expand=True, side="top")
        label57 = ttk.Label(labelframe11)
        label57.configure(foreground="#ff8040", text='此功能将清空所有数据')
        label57.pack(expand=True, side="top")
        label58 = ttk.Label(labelframe11)
        label58.configure(foreground="#ffff00", text='此功能将清空所有数据')
        label58.pack(expand=True, side="top")
        label59 = ttk.Label(labelframe11)
        label59.configure(foreground="#00ff00", text='此功能将清空所有数据')
        label59.pack(expand=True, side="top")
        label60 = ttk.Label(labelframe11)
        label60.configure(foreground="#00ffff", text='此功能将清空所有数据')
        label60.pack(expand=True, side="top")
        label61 = ttk.Label(labelframe11)
        label61.configure(foreground="#0000ff", text='此功能将清空所有数据')
        label61.pack(expand=True, side="top")
        label62 = ttk.Label(labelframe11)
        label62.configure(foreground="#8000ff", text='此功能将清空所有数据')
        label62.pack(expand=True, side="top")
        label63 = ttk.Label(labelframe11)
        label63.configure(foreground="#ff00ff", text='此功能将清空所有数据')
        label63.pack(expand=True, side="top")
        labelframe11.pack(fill="both", side="left")
        frame36.pack(expand=True, fill="both", side="top")
        notebook2.add(frame36, text='备份还原')
        self.sqlUserManageFrame = ttk.Frame(notebook2)
        self.sqlUserManageFrame.configure(height=200, width=200)
        self.sqlUserManageFrame.pack(side="top")
        notebook2.add(self.sqlUserManageFrame, text='用户管理')
        notebook2.pack(expand=True, fill="both", side="top")
        frame38.pack(side="top")
        self.tabView.add(frame38, text='数据库')
        self.aboutFrame = ttk.Frame(self.tabView)
        self.aboutFrame.configure(height=200, width=200)
        frame24 = ttk.Frame(self.aboutFrame)
        frame24.configure(height=200, width=200)
        separator3 = ttk.Separator(frame24)
        separator3.configure(orient="horizontal")
        separator3.place(
            anchor="nw",
            relwidth=1.0,
            relx=0.0,
            rely=0.50,
            x=0,
            y=0)
        frame32 = ttk.Frame(frame24)
        frame32.configure(height=200, width=200)
        frame33 = ttk.Frame(frame32)
        frame33.configure(height=200, width=200)
        frame31 = ttk.Frame(frame33)
        frame31.configure(height=200, width=200)
        frame1 = ttk.Frame(frame31)
        frame1.configure(height=200, width=200)
        label31 = ttk.Label(frame1)
        label31.configure(font="{黑体} 24 {}", text='背包编辑工具')
        label31.pack(expand=True, side="top")
        label46 = ttk.Label(frame1)
        label46.configure(text='开源Python数据库管理工具')
        label46.pack(anchor="e", side="top")
        label45 = ttk.Label(frame1)
        label45.configure(text='Copyright © 2023 By KY系应届生')
        label45.pack(anchor="e", side="top")
        frame1.pack(anchor="w", expand=True, side="right")
        frame31.pack(side="right")
        self.qrLabel = ttk.Label(frame33)
        self.qrLabel.configure(width=10)
        self.qrLabel.pack(anchor="e", expand=False, fill="both", side="right")
        frame33.pack(padx=20, side="top")
        frame32.pack(side="top")
        frame24.pack(anchor="n", expand=True, fill="x", side="top")
        label47 = ttk.Label(self.aboutFrame)
        label47.configure(
            foreground="#0080ff",
            text='仅用于Python开发学习交流，请勿将本项目技术或代码应用在恶意软件制作、软件著作权/知识产权盗取或不当牟利等非法用途中。')
        label47.pack(side="top")
        self.aboutFrame.pack(side="top")
        self.tabView.add(self.aboutFrame, text=' 关于 ')
        self.tabView.pack(expand=True, fill="both", side="top")
        #全局事件日志（背包编辑器与 PVF 编辑器的记录都进这里，位于窗口下方）
        self.logFrame = ttk.Labelframe(self.tabView.master, text='事件日志')
        self.logBar2 = ttk.Scrollbar(self.logFrame, orient="vertical")
        self.logBar2.pack(fill="y", side="right")
        self.logTextE = tk.Text(self.logFrame, height=12, takefocus=False, font=('微软雅黑', 11))
        self.logTextE.pack(expand=True, fill="both", side="left")
        self.logBar2.config(command=self.logTextE.yview)
        self.logTextE.config(yscrollcommand=self.logBar2.set)
        self.logFrame.pack(fill="x", side="bottom")
        setLogWidget(self.logTextE)
        log('欢迎使用背包编辑器!')
        self.tabView.bind(
            "<<NotebookTabChanged>>",
            self.change_TabView,
            add="")
        self.placeBtnFrame = ttk.Frame(self.tabFrame)
        self.placeBtnFrame.configure(height=20, width=220)
        self.refreshPKGBtn = tk.Button(self.placeBtnFrame)
        self.refreshPKGBtn.configure(
            borderwidth=0,
            overrelief="flat",
            relief="flat",
            text='刷新背包')
        self.refreshPKGBtn.pack(padx=3, side="left")
        self.stkSearchBtn = tk.Button(self.placeBtnFrame)
        self.stkSearchBtn.configure(
            borderwidth=0,
            overrelief="flat",
            relief="flat",
            text='道具搜索')
        self.stkSearchBtn.pack(padx=3, side="left")
        self.stkSearchBtn.configure(command=lambda:self._open_PVF_Editor('道具'))
        self.equSearchBtn = tk.Button(self.placeBtnFrame)
        self.equSearchBtn.configure(
            borderwidth=0,
            overrelief="flat",
            relief="flat",
            text='装备搜索')
        self.equSearchBtn.pack(padx=3, side="left")
        self.equSearchBtn.configure(command=lambda:self._open_PVF_Editor('装备'))
        self.placeBtnFrame.place(anchor="ne", height=23, relx=1.0, y=0)
        self.tabFrame.pack(expand=True, fill="both", side="top")
        separator2 = ttk.Separator(self.mainFrame)
        separator2.configure(orient="horizontal")
        separator2.pack(fill="x", side="top")
        frame4 = tk.Frame(self.mainFrame)
        frame4.configure(height=200, width=200)
        self.infoLabel = ttk.Label(frame4)
        self.infoSvar = tk.StringVar(value=' 欢迎使用背包编辑工具！')
        self.infoLabel.configure(
            borderwidth=1,
            text=' 欢迎使用背包编辑工具！',
            textvariable=self.infoSvar)
        self.infoLabel.pack(anchor="w", expand=True, fill="x", side="left")
        self.label6 = ttk.Label(frame4)
        self.versionSvar = tk.StringVar(value='当前软件版本：230903')
        self.label6.configure(
            anchor="e",
            borderwidth=1,
            text='当前软件版本：230903',
            textvariable=self.versionSvar)
        self.label6.pack(anchor="e", expand=False, fill="x", side="right")
        frame4.pack(fill="x", side="top")
        self.mainFrame.pack(expand=True, fill="both", side="top")




        # Main widget
        self.mainwindow = self.mainFrame
        self.w:tk.Tk = master
        self.root = master
        self.style = style

        self.check_update_flg = check_update
        self.title = self.w.title
        self._build()
        #self.mainwindow.after(10,self._build)
    
    def _build(self):
        def treeview_sortColumn(col,tree):
            nonlocal reverseFlag,sortQueue                         # 定义排序标识全局变量
            sortID = len(sortQueue)
            sortQueue.append(sortID)
            lst = [(tree.set(itemStr,col),itemStr)
                    for itemStr in tree.get_children("")]
            lst_int = []
            useInt = True
            for itemStr in tree.get_children(""):
                value = tree.set(itemStr,col).replace(',','')
                try:
                    if value in ['paycoin', 'money','cera','cera_point']:
                        #print(value)
                        value = 0
                    value = int(value)
                    lst_int.append([value,itemStr])
                except:
                    useInt = False
                    break
            if useInt:
                lst = lst_int
            #print(lst)                                 # 打印列表
            lst.sort(key=lambda x:x[0] if isinstance(x[0],int) else x[0].encode('gbk',errors='replace'),reverse=reverseFlag)              # 排序列表
            #print(lst)                                 # 打印列表
            reverseFlag = not reverseFlag              # 更改排序标识
            for index, item in enumerate(lst):         # 重新移动项目内容
                if len(sortQueue)>sortID+1:
                    break
                tree.move(item[1],"",index)
                if index%300==0:
                    self.mainwindow.update()
        
        self.password = ''
        self.CONNECTING_FLG = False #判断正在连接
        self.PVF_LOADING_FLG = False #判断正在加载pvf
        self.PVF_EDIT_OPEN_FLG = False
        self.fillingFlg = False #填充treeview
        self.currentItemDict = {}
        self.editedItemsDict = {}
        self.itemInfoClrFuncs = {}
        self.selectedCharacItemsDict = {}   #使用tabName存储id:ItemSlot
        self.fillTreeFunctions = {}
        self.updateMagicSealFuncs = {}
        self.editFrameUpdateFuncs = {}
        self.globalCharacBlobs = {} #利用标签页名字来存储原始blob
        self.globalCharacNonBlobs = {} #利用标签页名字来存储原始非blob
        self.unknowItemsListDict = {}
        self.errorItemsListDict = {}
        self.errorInfoDict = {}
        self.importFlgDict = {} #保存导入过的标签页名
        self.orbTypeEList = []
        self.itemsTreevs_now = {}

        self.loadPkgTaskList = []
        self.currentTreeViews = {}
        self.editFrameShowFuncs = {}
        self.blobCommitExFunc = lambda cNo=0:...
        self.tabIDDict = tabIDDict
        self.titleString = f'背包编辑工具 - [在线人数][NA/NA]'

        self.tabViewChangeFuncs = []    #切换tab时执行的function列表
        self.tabNames = []
        self.cNo = 0    #当前操作的Cno
        self.uid = 0
        self.cName = ''
        self.lev = 0
        self.inventory_capacity = 0 # 0表示没有扩充，16表示扩充两行
        self.characInfos = {}
        positionDict = {
            0x00:['快捷栏',[3,9]],
            0x01:['装备',[9,57]],
            0x02:['消耗品',[57,105]],
            0x03:['材料',[105,153]],
            0x04:['任务材料',[153,201]],
            0x05:['宠物',[98,99]],#正在使用的宠物
            0x06:['宠物装备',[0,49],[99,102]],#装备栏和正在使用的装备
            0x07:['宠物消耗品',[49,98],[0,0]],
            0x0a:['副职业',[201,249]]
        }
        self.positionDict = positionDict
        self.pool = None

        try:
            self.w.iconbitmap(IconPath)
        except:
            self.w.call('wm', 'iconphoto', self.w._w, tk.PhotoImage(file=IconPath))
        

        self.HDresolutionBtn.destroy()
        
        self.pvfToolBtn.destroy()

        self._buildSqlConn()
        self._buildtab_main()
        self.blobTabNameList = list(globalBlobs_map.keys())
        self.blobFrameList = [self.invFrame,self.equFrame,self.creatureFrame,self.cargoFrame,self.accountCargoFrame]
        
        
        self.nonBlobFrameList = [self.creatureItemFrame,self.avatarFrame,self.mailFrame]
        self.blobFrameWids = []
        for i,frame in enumerate(self.blobFrameList):
            tabName = self.blobTabNameList[i]
            itemEditFrame = itemSlotFrame.ItemslotframeWidget(frame)
            self.blobFrameWids.append(itemEditFrame)
            self._buildtab_itemTab(itemEditFrame,tabName)
        self.mailFrame = mailFrame.MailframeWidget(self.mailFrame)
        self.avatarFrame = avatarFrame.AvatarframeWidget(self.avatarFrame)
        self.creatureItemFrame = creatureFeame.CreatureframeWidget(self.creatureItemFrame)
        self.questFrame = questFrame.QuestframeWidget(self.questFrame,self)
        self.sqlUserManageF = sqlUserManager.SqluserframeWidget(self.sqlUserManageFrame)
        
        for tab in self.tabView.tabs():
            tabName = self.tabView.tab(tab,'text')
            tabIDDict[tabName] = tab

        self._buildtab_itemTab_creature(self.creatureItemFrame)
        self._buildtab_itemTab_avatar(self.avatarFrame)
        self._buildtab_itemTab_mail(self.mailFrame)
        self._buildtab_GM()
        self._buildTab_bubble()
        self._buildFrame_SSH()
        self._buildTab_Baned()

        
        self._buildtab_charac(self,' 其它 ')

        sortQueue = []
        reverseFlag = True

        for tree in list(self.itemsTreevs_now.values()) + [self.characTreeV,self.banedTreeV]:
            for colIndex in range(20):
                try:
                    col = tree.column(colIndex)['id']
                    tree.heading(f"#{colIndex+1}", command=lambda c=col,t=tree:treeview_sortColumn(c,t))
                    #print(colIndex,col)
                except:
                    break
        
        boxs = [self.characTreeV,self.creatureItemFrame.itemsTreev_now,self.avatarFrame.itemsTreev_now,self.mailFrame.itemsTreev_now,self.banedTreeV]
        bars = [self.characBar,self.creatureItemFrame.itemsTreev_bar,self.avatarFrame.itemsTreev_bar,self.mailFrame.itemsTreev_bar,self.banedBar]

        for i in range(len(boxs)):
            box:tk.Listbox = boxs[i]
            bar = bars[i]
            bar.config(command=box.yview)
            box.config(yscrollcommand=bar.set)
        
        self.db_ipE.config(values=list(cacheM.config.get('DB_CONFIGS').keys()))
        self.db_pwdE.config(values=['123456','uu5!^%jg'])
        VERSION = '230915'
        self.versionSvar.set(f'当前软件版本：{VERSION}  ')

        self.create_CXV()
        self.get_online_num()


        qrCodeStr = 'https://jq.qq.com/?_wv=1027&k=vMnki7kh'
        code=pyqrcode.create(qrCodeStr)#需要显示中文encoding='UTF-8'即可
        cXbm=code.xbm(scale=2)#scale生成的二维码图片比例大小
        self.qrCode=tk.BitmapImage(data=cXbm)
        self.qrCode.config(foreground="black")
        self.qrLabel.configure(image=self.qrCode)

        theme = cacheM.config.get('THEME','默认主题')
        self.themeE.set(value=theme)
        themes = ['默认主题','亮-cosmo','亮-flatly','亮-journal','亮-litera','亮-minty','亮-morph','暗-cyborg','暗-darkly','暗-solar']
        self.themeE.config(values=themes,state='readonly')



    def _buildSqlConn(self):
        #数据库连接
        db_ip = self.db_ipE
        db_ip.insert(0,cacheM.config['DB_IP'])
        db_port = self.db_portE
        db_port.insert(0,cacheM.config['DB_PORT'])
        db_user = self.db_userE
        db_user.insert(0,cacheM.config['DB_USER'])
        db_pwd = self.db_pwdE
        self.password = cacheM.config['DB_PWD']
        db_pwd.insert(0,'******')


