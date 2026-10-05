'''动作与工具：PVF 编辑器、搜索提交、数据库备份（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppActions:
    def open_PVF_Cache_Edit(self):
        def quit_edit():
            pvfEditMainWin.destroy()
            self.PVF_CACHE_EDIT_OPEN_FLG = False
        def update_pvf_cache_sel():
            res = []
            for MD5,infoDict in cacheM.cacheManager.tinyCache.items():
                if not isinstance(infoDict,dict):continue
                res.append(f'{infoDict["nickName"]}-{MD5}')
            self.PVFCacheE.config(values=res)
            pvfMD5 = self.PVFCacheE.get().split('-')[-1]
            if len(pvfMD5)>0:
                if cacheM.cacheManager.tinyCache.get(pvfMD5) is None:
                    self.PVFCacheE.set(f'请选择PVF缓存')
                else:
                    self.PVFCacheE.set(f'{cacheM.cacheManager.tinyCache[pvfMD5].get("nickName")}-{pvfMD5}')
            print('PVF缓存已保存')
        from dnfpkgtool.pvfCacheFrame import PVFCacheCfgFrame
        if self.PVF_CACHE_EDIT_OPEN_FLG:
            self.pvfEditWin.state('normal')
            self.pvfEditWin.focus_force()
            self.cacheEditFrame.fillTree()
            return False
        self.PVF_CACHE_EDIT_OPEN_FLG = True
        pvfEditMainWin = tk.Toplevel(self.tabView)
        self.pvfEditWin = pvfEditMainWin
        pvfEditMainWin.iconbitmap(IconPath)
        pvfEditFrame = PVFCacheCfgFrame(pvfEditMainWin,closeFunc=quit_edit,saveFunc=update_pvf_cache_sel)
        pvfEditFrame.pack(fill=tk.BOTH,expand=True,anchor=tk.N)
        pvfEditMainWin.bind('<Escape>',pvfEditFrame.quitter)
        self.cacheEditFrame = pvfEditFrame
        pvfEditMainWin.protocol('WM_DELETE_WINDOW',quit_edit)
        pvfEditMainWin.title('PVF缓存管理')
        pvfEditMainWin.resizable(False,True)
        self.PVFEditWinFrame = pvfEditFrame
    def _open_PVF_Editor(self,tab=''):
        def quit():
            self.PVF_EDIT_OPEN_FLG=False
            self.PVFToolWin.destroy()
        
        if self.PVF_EDIT_OPEN_FLG:
            self.PVFToolWin.state('normal')
            self.PVFToolWin.focus_force()
            if tab:
                self.PVFTool.select_Tab(tab)
            return False
        PVFToolMainWin = tk.Toplevel(self.stkSearchBtn)
        
        self.PVFToolWin = PVFToolMainWin
        self.PVFTool = pvfEditorGUI.PvfeditmainframeApp(self.PVFToolWin,
                                                         onSubmitBag=self.submit_Search_to_Bag,
                                                         onSubmitMail=self.submit_Search_to_Mail,
                                                         onLoadEdit=self.submit_Search_to_Edit,
                                                         logFunc=log)
        self.PVF_EDIT_OPEN_FLG = True
        PVFToolMainWin.title('PVF编辑器 测试版')
        PVFToolMainWin.iconbitmap(IconPath)
        PVFToolMainWin.protocol('WM_DELETE_WINDOW',quit)
        if tab:
            self.PVFTool.select_Tab(tab)

    def submit_Search_to_Bag(self,itemID):
        '''把搜索结果提交到背包物品编辑框（原"专用搜索"的提交编辑）'''
        try:
            tabName = self.pkgTab.tab(self.pkgTab.select())['text']
        except:#首标签末尾无数字
            return False
        itemSlot = sqlM.DnfItemSlot(b'\x00'*61)
        itemSlot.id = itemID
        itemSlot.type = 0x01
        itemSlot.durability = 999
        itemSlot.oriBytes = itemSlot.build_bytes()
        try:
            self.editFrameUpdateFuncs[tabName](itemSlot)
            self.w.focus_force()
            self.tabView.select(self.tabIDDict.get(' 背包 '))
        except:
            pass

    def submit_Search_to_Mail(self,itemID):
        '''把搜索结果提交到邮件（原"专用搜索"的提交邮件）'''
        self.itemIDEntry.delete(0,tk.END)
        self.itemIDEntry.insert(0,itemID)
        self.readSlotID()
        self.tabView.select(self.tabIDDict.get(' 邮件 '))

    def submit_Search_to_Edit(self,itemID):
        '''把搜索结果载入背包页签的"修改物品"控件：搜索与修改共用同一处搜索，不必再手输物品名'''
        try:
            tabName = self.pkgTab.tab(self.pkgTab.select())['text']
        except Exception:
            return False
        itemEditFrame = getattr(self,'itemEditFrameDict',{}).get(tabName)
        if itemEditFrame is None:
            return False
        itemSlot = sqlM.DnfItemSlot(b'\x00'*61)
        itemSlot.id = itemID
        itemSlot.type = 0x01
        itemSlot.durability = 999
        itemSlot.oriBytes = itemSlot.build_bytes()
        self.tabView.select(self.tabIDDict.get(' 背包 '))
        try:
            #fillItemEditFrame：把这件物品的完整数据填进"修改物品"控件，改完再点提交才会写库
            self.editFrameUpdateFuncs[tabName](itemSlot)
            itemEditFrame.itemIDEntry.config(state='normal')
            itemEditFrame.itemIDEntry.delete(0,tk.END)
            itemEditFrame.itemIDEntry.insert(0,itemID)
            itemEditFrame.itemNameEntry.delete(0,tk.END)
            itemEditFrame.itemNameEntry.insert(0,str(cacheM.ITEMS_dict.get(int(itemID),'')))
        except Exception as e:
            log('载入物品数据失败：%r' % e)
            return False
        log('搜索面板载入修改物品数据：物品[%s][%s]' % (cacheM.ITEMS_dict.get(int(itemID)),itemID))
        return True


    def check_Update(self):
        ...

    def checkBloblegal(self):
        positionDict = self.positionDict
        if len(cacheM.PVFcacheDict.keys())==0:
            return 'PVF未加载'
        for tabName in self.globalCharacBlobs.keys():
            itemDict = self.selectedCharacItemsDict[tabName]
            self.unknowItemsListDict[tabName] = []  #保存位置物品的index
            self.errorItemsListDict[tabName] = []   #保存错误物品的index
            self.errorInfoDict[tabName] = {}    #保存错误信息
            for index, itemSlot in itemDict.items():
                itemSlot:sqlM.DnfItemSlot
                if itemSlot.id==0:
                    continue
                self.errorInfoDict[tabName][index] = ''
                attach_type = cacheM.get_Item_Info_In_Dict(itemSlot.id).get('[attach type]',[''])
                if itemSlot.isSeal==1 and cacheM.PVFcacheDict['stackable_detail'].get(itemSlot.id) is None:
                    if attach_type is not None and attach_type[0]!='[sealing]':
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品封装状态冲突-当前为封装 \n'
                if attach_type[0]!='[sealing]' and itemSlot.sealCnt!=0:
                    self.errorItemsListDict[tabName].append(index)
                    self.errorInfoDict[tabName][index] += f'物品封装次数冲突-当前不为0 \n'
                typeID,typeZh = cacheM.getStackableTypeMainIdAndZh(itemSlot.id)
                #print(typeID,typeZh,cacheM.ITEMS_dict.get(itemSlot.id))
                #常规判断，标记种类是否与实际种类冲突
                
                if typeID not in [0,1,2,3,4,5,6,7,0x0a]:
                    self.errorItemsListDict[tabName].append(index)
                    self.errorInfoDict[tabName][index] += f'物品种类冲突-当前{typeID,typeZh}-不属于此列表分类 \n'
                if typeID!=0 and typeID!=itemSlot.type:
                    self.errorItemsListDict[tabName].append(index)
                    self.errorInfoDict[tabName][index] += f'物品种类冲突-当前{itemSlot.type}-{typeID} \n'
                elif typeID==0:
                    self.unknowItemsListDict[tabName].append(index)
                stkLimit = None
                pvfInfoDict = cacheM.get_Item_Info_In_Dict(itemSlot.id)
                if pvfInfoDict is not None:
                    stkLimit = pvfInfoDict.get('[stack limit]')
                    if stkLimit is not None:
                        stkLimit = stkLimit[0]
                if stkLimit is not None and stkLimit<itemSlot.num_grade:
                    self.errorItemsListDict[tabName].append(index)
                    self.errorInfoDict[tabName][index] += f'物品数量错误-当前{itemSlot.num_grade}-{stkLimit} \n'

                if tabName=='物品栏' and typeID!=0:
                    startIndex,endIndex = positionDict[typeID][1]
                    endIndexNew = endIndex - (16-self.inventory_capacity)
                    if index in range(startIndex,endIndexNew) or index in [3,4,5,6,7,8]:
                        pass
                    elif index in range(endIndexNew,endIndex):
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品位置错误-当前{index}-{[startIndex,endIndexNew-1]}-角色物品槽需扩充 \n'
                    else:
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品位置错误-当前{index}-{[startIndex,endIndexNew-1]} \n'
                elif tabName=='穿戴栏':
                    if typeID != 0x01:
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品种类错误-当前{typeID}-0x01 \n'
                    if itemSlot.isSeal==1:
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品封装错误-当前{itemSlot.isSeal}-0x00 \n'
                elif tabName=='宠物栏':
                    try:
                        if index in range(*positionDict[typeID][1]) or index in range(*positionDict[typeID][2]):
                            pass
                        else:
                            self.errorItemsListDict[tabName].append(index)
                            self.errorInfoDict[tabName][index] += f'物品位置错误-当前{index}-{positionDict[typeID][1],positionDict[typeID][2]} \n'
                    except:
                        print('宠物栏',index,typeID)
                elif tabName==' 仓库 ':
                    if itemSlot.type not in [1,2,3,0x0a]:
                        self.errorItemsListDict[tabName].append(index)
                        self.errorInfoDict[tabName][index] += f'物品类型错误-当前{itemSlot.type}-{[1,2,3,0x0a]} '
        print('未知物品',self.unknowItemsListDict,'\n错误物品',self.errorItemsListDict)

    def change_Theme(self, event=None):
        theme = self.themeE.get()
        currentTheme = cacheM.config.get('THEME','默认主题')
        if theme == currentTheme:
            return False
        if theme=='默认主题':
            messagebox.showinfo('提示','已切换至默认主题，重启后生效')
            cacheM.config['THEME'] = '默认主题'
            cacheM.save_config()
        else:
            
            theme = theme.split('-')[-1]
            messagebox.showinfo('提示','已切换至'+theme+'主题，重启后生效')
            cacheM.config['THEME'] = theme
            cacheM.save_config()
        pass

    def sel_IP(self, event=None):
        ip = self.db_ipE.get()
        if cacheM.config.get('DB_CONFIGS').get(ip) is not None:
            port = cacheM.config.get('DB_CONFIGS').get(ip)['port']
            pwd = cacheM.config.get('DB_CONFIGS').get(ip)['pwd']
            user = cacheM.config.get('DB_CONFIGS').get(ip)['user']
            self.db_portE.delete(0,tk.END)
            self.db_portE.insert(0,port)
            self.db_pwdE.set(pwd)
            self.db_userE.delete(0,tk.END)
            self.db_userE.insert(0,user)


    def search_Account(self):
        self.search_Account_()


    def search_Charac(self):
        self.search_Charac_()


    def sel_Sql_Encode(self, event=None):
        self.sel_Sql_Encode_()


    def sel_PVF_Cache(self, event=None):
        self.load_PVF(self.PVFCacheE.get().split('-')[-1])


    def openPVF(self):
        self.load_PVF('')

    @inThread
    def selectCharac(self, event=None):
        t = self.selectCharac_(True)
        t.join()
    def change_TabView(self, e=None):
        for func in self.tabViewChangeFuncs:
            func(e)
    
    def create_CXV(self):
        for tabName,tree in self.currentTreeViews.items():
            if tabName not in ['物品栏','穿戴栏','宠物栏',' 仓库 ','账号金库']:
                continue
            creat_cxv_pkg(tree,self,tabName)
    
    @inThread
    def get_online_num(self):
        while True:
            try:
                if self.onlineNumVar.get()==0:
                    self.titleString = f'背包编辑工具 - [在线人数实时更新已关闭][泡点已关闭]'
                    time.sleep(5)
                    continue
                self.onlineUIDCNos = sqlM.get_online_charac_3()
                self.onlineCNos = [item[1] for item in self.onlineUIDCNos]
                self.onlinePlayerUIDCnos = []
                self.onlineBotUIDCnos = []
                botNum = 0
                playerNum = 0
                for uid,cNo,ipaddr in self.onlineUIDCNos:
                    if ipaddress.ip_address(ipaddr.strip()).is_private:
                        botNum+=1
                        self.onlineBotUIDCnos.append((uid,cNo,ipaddr))
                    else:
                        playerNum+=1
                        self.onlinePlayerUIDCnos.append((uid,cNo,ipaddr))
                self.titleString = f'背包编辑工具 - [内网/外网在线][{len(self.onlineBotUIDCnos)}/{len(self.onlinePlayerUIDCnos)}]'
            except Exception as e:
                pass
            time.sleep(5)


    def fill_db_bak(self):
        self.db_list = ['taiwan_cain','taiwan_cain_2nd','taiwan_billing','d_taiwan','d_channel','d_guild','d_taiwan_secu','d_technical_report',
               'taiwan_cain_auction_gold','taiwan_cain_auction_cera','taiwan_cain_log','taiwan_cain_web','taiwan_game_event',
               'taiwan_mng_manager','taiwan_prod','taiwan_se_event','taiwan_login','taiwan_login_play']#'taiwan_pvp',,'taiwan_siroco'
        allDB = sqlM.execute_and_fetch('taiwan_cain','show databases;')
        allDB = [db[0] for db in allDB]
        self.db_avaliable = []
        for db in self.db_list:
            if db in allDB:
                self.db_avaliable.append(db)
        self.remoteSqlTree.delete(*self.remoteSqlTree.get_children())
        for db in self.db_avaliable:
            self.remoteSqlTree.insert('',tk.END,values=[db,'未备份'])

    @inThread
    def init_db(self):
        bakPath = 'sql_bak/初始数据库'
        if not messagebox.askokcancel('初始化确认','确认初始化数据库？当前数据库中所有存档将被清空，仅保留运行所需数据！'):
            return False
        self.localSqlTree.delete(*self.localSqlTree.get_children())
        files = os.listdir(bakPath)
        bakFiles = []
        for file in files:
            if file.endswith('.sqlbak'):
                bakFiles.append(file[:-7])
        self.db_bak_files = bakFiles
        self.bakPath = bakPath
        for fileName in bakFiles:
            self.localSqlTree.insert('',tk.END,values=[fileName,'待还原'])
        
        for item in self.localSqlTree.get_children():
            self.localSqlTree.selection_add(item)
        self.restore_sel_db()
        

    def sel_all_remote_db(self):
        for line in self.remoteSqlTree.get_children():
            self.remoteSqlTree.selection_add(line)

    @inThread
    def backup_sel_db(self):
        def read_bak_stat():
            for line in self.remoteSqlTree.get_children():
                db = self.remoteSqlTree.item(line)['values'][0]
                if db in selDBList:
                    bakNum = len(sqlM.db_bak_stat.get(db,{}).get('bak',[]))
                    totalNum = len(sqlM.db_bak_stat.get(db,{}).get('total',[]))
                    if bakNum<totalNum:
                        self.remoteSqlTree.item(line,values=[db,f'[备份中 {bakNum}/{totalNum}]'])
                    elif totalNum==0:
                        self.remoteSqlTree.item(line,values=[db,f'等待备份'])
                    else:
                        self.remoteSqlTree.item(line,values=[db,f'备份完成({bakNum})'])
        bakPath = 'sql_bak'
        dateStr = datetime.datetime.now().strftime('%Y-%m-%d')
        bakPath = os.path.join(bakPath,self.db_ipE.get()+f'_{dateStr}')
        if not os.path.exists(bakPath):
            os.makedirs(bakPath)
        sels = self.remoteSqlTree.selection()
        selDBList = []
        for sel in sels:
            selDBList.append(self.remoteSqlTree.item(sel)['values'][0])
        if not messagebox.askokcancel('确认备份',f'确认备份选中的{len(selDBList)}个数据库？{selDBList}？\n数据库将被被分到目录{bakPath}下'):
            return False
        
        if sqlM.bak_db_num != sqlM.total_bak_db_num:
            messagebox.showerror('功能正忙','请等待当前备份任务结束')
            return False
        sqlM.bak_db_num = 0
        sqlM.total_bak_db_num = len(selDBList)
        for db in selDBList:
            sqlM.backup_db(db,bakPath)
        while sqlM.total_bak_db_num>sqlM.bak_db_num:
            read_bak_stat()
            time.sleep(1)
        read_bak_stat()
        messagebox.showinfo('备份完成',f'备份完成，共备份{sqlM.total_bak_db_num}个数据库')
    

    def open_db_bak_dir(self):
        self.localSqlTree.delete(*self.localSqlTree.get_children())
        bakPath = askdirectory(title='选择备份文件夹',initialdir='sql_bak')
        if bakPath=='':
            return False
        print(f'打开备份文件夹{bakPath}')
        files = os.listdir(bakPath)
        bakFiles = []
        for file in files:
            if file.endswith('.sqlbak'):
                bakFiles.append(file[:-7])
        self.db_bak_files = bakFiles
        self.bakPath = bakPath
        for fileName in bakFiles:
            self.localSqlTree.insert('',tk.END,values=[fileName,'待还原'])

    @inThread
    def restore_sel_db(self):
        def read_restore_stat():
            for line in self.localSqlTree.get_children():
                db = self.localSqlTree.item(line)['values'][0]
                if db in selDBList:
                    restoredNum = len(sqlM.db_restore_stat.get(db,{}).get('restored',[]))
                    totalNum = len(sqlM.db_restore_stat.get(db,{}).get('total',[]))
                    if restoredNum<totalNum:
                        self.localSqlTree.item(line,values=[db,f'[还原中 {restoredNum}/{totalNum}]'])
                    elif totalNum==0:
                        self.localSqlTree.item(line,values=[db,f'等待还原'])
                    else:
                        self.localSqlTree.item(line,values=[db,f'还原完成({restoredNum})'])
        sels = self.localSqlTree.selection()
        selDBList = []
        for sel in sels:
            selDBList.append(self.localSqlTree.item(sel)['values'][0])
        if not messagebox.askokcancel('确认还原',f'确认还原选中的{len(selDBList)}个数据库？\n请停止游戏服务端并关闭其他链接以保证还原正常进行。\n{selDBList}'):
            return False
        if sqlM.restore_db_num != sqlM.total_restore_db_num:
            messagebox.showerror('功能正忙','请等待当前还原任务结束')
            return False
        sqlM.restore_db_num = 0
        sqlM.total_restore_db_num = len(selDBList)
        for db in selDBList:
            sqlM.restore_db(db,self.bakPath)
        while sqlM.total_restore_db_num>sqlM.restore_db_num:
            read_restore_stat()
            time.sleep(0.3)
            self.mainFrame.update()

        read_restore_stat()
        messagebox.showinfo('还原完成',f'还原完成，共还原{sqlM.total_restore_db_num}个数据库')
        

