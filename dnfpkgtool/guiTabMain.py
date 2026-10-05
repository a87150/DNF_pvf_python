'''主界面/物品栏页签（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppTabMain:
    def _buildtab_main(self):
        def fill_charac_treeview(charac_list):
            self.characTreeV.delete(*self.characTreeV.get_children())
            for values in charac_list:
                uid,cNo,name,lev,job,growType,deleteFlag,expert_job = values
                jobDict = cacheM.jobDict.get(job)
                if isinstance(jobDict,dict):
                    jobNew = jobDict.get(growType % 16)
                else:
                    jobNew = growType % 16
                self.characTreeV.insert('',tk.END,values=[cNo,name,lev,jobNew,uid],tags='deleted' if deleteFlag==1 else '')
                self.characInfos[cNo] = {'uid':uid,'name':name,'lev':lev,'job':job,'growType':growType,'expert_job':expert_job} 
            self.SqlEncodeE.set(f'{sqlM.sqlEncodeUseIndex}-{sqlM.SQL_ENCODE_LIST[sqlM.sqlEncodeUseIndex]}')
            self.clear_charac_tab_func()
            self.currentItemDict = {}
            self.selectedCharacItemsDict = {}
            for tabName in self.itemInfoClrFuncs.keys():
                itemsTreev_now = self.itemsTreevs_now[tabName]
                itemsTreev_now.delete(*itemsTreev_now.get_children())
                try:
                    self.itemInfoClrFuncs[tabName]()    #清除物品信息显示
                    self.fillTreeFunctions[tabName]()   #填充treeview
                except:
                    pass
                try:
                    itemsTreev_del = self.itemsTreevs_del[tabName]
                    itemsTreev_del.delete(*itemsTreev_del.get_children())
                except:
                    continue
            self.globalCharacBlobs = {}

        def searchCharac(searchType='account'):   #或者cName
            if searchType=='account':
                characs = sqlM.getCharacterInfo(uid=sqlM.getUID(self.aNameE.get()))
                try:
                    uid = int(self.aNameE.get())
                    characs_uid = sqlM.getCharacterInfo(uid=uid)
                    characs += characs_uid
                except:
                    pass
                
            else:
                if self.cNameE.get()=='':
                    characs = sqlM.get_online_charac()
                else:
                    characs = sqlM.getCharacterInfo(cName=self.cNameE.get())
            print('加载角色列表',characs)
            fill_charac_treeview(charac_list=characs)

        @inThread
        def selectCharac(showTitle=False):
            
            if len(self.characTreeV.selection())==0:return
            taskID = len(self.loadPkgTaskList)
            self.loadPkgTaskList.append(taskID)
            self.fillingFlg = True
            sel = self.characTreeV.item(self.characTreeV.selection()[0])['values']
            try:
                cNo, cName, lev, job, uid = sel
            except:
                print('未选择角色')
                return False
            if self.PVF_LOADING_FLG:
                print('等待PVF加载中')
                return False
            if len(cacheM.ITEMS_dict.keys())<10:
                print(f'请选择物品列表来源')
                return False
            log(f'加载角色物品[{sel}]')
            inventory, equipslot, creature, inventory_capacity = sqlM.getInventoryAll(cNo=cNo)[0]
            cargo,jewel,expand_equipslot = sqlM.getCargoAll(cNo=cNo)[0]
            creature_items = sqlM.getCreatureItem(cNo=cNo)
            user_items = sqlM.getAvatar(cNo=cNo,ability_=True)
            account_cargo = sqlM.get_Account_Cargo(cNo=cNo)
            user_postals = sqlM.get_postal_new(cNo=cNo)
            #print(user_postals)
            if showTitle:
                print(f'角色[{cName}]物品已加载')
            else:
                log(f'角色[{cName}]物品已加载')
            #self.enable_Tabs()
            blobsItemsDict = {}
            for key,name in globalBlobs_map.items():
                blobsItemsDict[key] = locals()[name]
            self.globalCharacBlobs = blobsItemsDict

            nonBlobItemsDict = {}
            for key,name in globalNonBlobs_map.items():
                nonBlobItemsDict[key] = locals().get(name)
            self.cNo = cNo
            self.cName = cName
            #self.job = job
            self.uid = uid
            self.lev = lev
            self.inventory_capacity = inventory_capacity
            self.invCapacityE.set(f'{inventory_capacity}')
            self.globalCharacNonBlobs = nonBlobItemsDict
            self.importFlgDict = {}
            #print('填充treev')
            self.w.after(1,lambda:self.fill_tab_treeviews(taskID))
            self.fill_charac_tab_fun()
            while self.fillingFlg and len(self.loadPkgTaskList)==taskID+1:
                time.sleep(0.01)
                #print(self.fillingFlg)
            self.update_GM()
            

        def loadPVF(pvfPath:str=''):
            '''设置物品来源，读取pvf或者csv'''
            def inner():
                nonlocal pvfPath
                print('数据源加载中...PVF：',pvfPath)
                if cacheM.config.get('PVF_PATH')== '':
                    messagebox.showinfo('PVF 文件位置','PVF 文件（Script.pvf）在服务器上的路径：\n/home/neople/game/Script.pvf\n\n请先把该文件下载到本机，再选择打开。')
                if self.PVF_LOADING_FLG:
                    print('等待PVF加载')
                    return False
                if pvfPath=='':
                    pvfPath = askopenfilename(filetypes=[('DNF Script.pvf file','*.pvf')])
                if pvfPath!='':
                    cacheM.pvfReader.LOAD_FUNC = cacheM.pvfReader.get_Item_Dict
                    t1 = time.time()
                    print('加载PVF中...')
                    self.PVF_LOADING_FLG = True
                    try:
                        info = cacheM.loadItems2(True,pvfPath,encode=self.PVFEncodeE.get())
                    except Exception as e:      #加载线程里的异常原本没人看得到，这里记进全局日志
                        self.PVF_LOADING_FLG = False
                        import traceback
                        log('PVF加载失败：%s' % traceback.format_exc())
                        messagebox.showerror('PVF加载失败', traceback.format_exc()[-800:])
                        return False
                    self.PVF_LOADING_FLG = False
                    t = time.time() - t1 
                    MD5 = cacheM.PVFcacheDict.get("MD5")
                    if MD5 is None:
                        return False
                    info += '  花费时间%.2fs' % t
                    self.PVFCacheE.set(f'{cacheM.tinyCache[MD5].get("nickName")}-{MD5}')
                    self.PVFEncodeE.set(cacheM.tinyCache[MD5].get("encode"))

                    # 更新魔法封印框、时装潜能框和职业框
                    if cacheM.magicSealDict.get(0) is None:
                        cacheM.magicSealDict[0] = ''
                    [func() for func in self.updateMagicSealFuncs.values()]
                    self.hiddenCom.config(values=['0-None']+[f'{i+1}-{value}' for i,value in enumerate(cacheM.avatarHiddenList[0])])
                    self.jobE.config(values=[f'{item[0]}-{item[1][0]}'  for item in cacheM.jobDict.items()])
                    self.jobE.set('')

                    PVFres = []
                    for MD5,infoDict in list(cacheM.cacheManager.tinyCache.items()):
                        if not isinstance(infoDict,dict):continue
                        PVFres.append(f'{cacheM.cacheManager.tinyCache[MD5]["nickName"]}-{MD5}')
                    self.PVFCacheE.config(values=PVFres)
                    enhanceTypes = list(cacheM.enhanceDict_zh.keys())
                    for orbTypeE in self.orbTypeEList:
                        orbTypeE.config(values=enhanceTypes)

                    if self.PVF_CACHE_EDIT_OPEN_FLG:
                        self.PVFEditWinFrame.fillTree()
                    print(info)
                else:
                    print('PVF路径为空，加载CSV')
                    cacheM.loadItems2(False)
                    self.PVFCacheE.set('使用CSV')
                selectCharac()
            t = threading.Thread(target=inner)
            t.daemon = True
            t.start()
            
        self.load_PVF = loadPVF

        #账号查询功能
        self.search_Account_ = lambda e=None:searchCharac('account')
        self.search_Charac_ = lambda e=None:searchCharac('cName')
        self.selectCharac_ = selectCharac
        self.fillCharac = fill_charac_treeview
        self.refreshPKGBtn.config(command=self.selectCharac_)
        searchFrame = self.searchFrame
        

        self.connectorE.set('----')
        self.SqlEncodeE.config(values=[f'{i}-{encode}' for i,encode in enumerate(sqlM.SQL_ENCODE_LIST)],state='readonly')
        self.SqlEncodeE.set('----')
        def setEncodeing(e=None):
            encodeIndex = int(self.SqlEncodeE.get().split('-')[0])
            sqlM.sqlEncodeUseIndex = encodeIndex
            sqlM.ENCODE_AUTO = False  #关闭自动编码切换
        self.sel_Sql_Encode_ = setEncodeing


        res = []
        for MD5,infoDict in list(cacheM.cacheManager.tinyCache.items()):
            if not isinstance(infoDict,dict):continue
            res.append(f'{cacheM.cacheManager.tinyCache[MD5]["nickName"]}-{MD5}')
        self.PVFCacheE.config(values=res,state='readonly')

        self.PVFCacheE.set('PVF缓存')
        self.PVFEncodeE.config(values=['big5','gbk','utf-8'],state='readonly')
        self.PVFEncodeE.set('big5')

        CreateToolTip(self.PVFEncodeE,'PVF编码，加载乱码请尝试修改后重新加载')

        characTreev = self.characTreeV
        characTreev.tag_configure('deleted', background='gray')



    def _buildtab_itemTab(self,itemEditFrame:itemSlotFrame.ItemslotframeWidget,tabName):
        #登记各背包子页签的"修改物品"控件，供搜索面板的"载入修改"直接填进来
        if not hasattr(self,'itemEditFrameDict'):
            self.itemEditFrameDict = {}
        self.itemEditFrameDict[tabName] = itemEditFrame
        def ask_commit():
            if showSelectedItemInfo()!=True or self.cNo==0:
                return False
            if not messagebox.askokcancel('修改确认',f'确定修改{tabName}所选物品？\n请确认账号不在线或正在使用其他角色\n{self.editedItemsDict[tabName]}'):
                return False
            cNo = self.cNo
            key = globalBlobs_map[tabName]
            originblob = self.globalCharacBlobs[tabName]
            #print(originblob,self.editedItemsDict[tabName],cNo,key)
            sqlM.commit_change_blob(originblob,self.editedItemsDict[tabName],cNo,key)
            print(f'修改列表{tabName}-{self.editedItemsDict[tabName]}')
            self.blobCommitExFunc(self.cNo)
            print(f'====修改成功==== {tabName} 角色ID：{self.cNo}')
            return self.selectCharac()
            
        def save_blob(fileType='blob',additionalTag=tabName):
            filePath = asksaveasfilename(title=f'保存文件(.{fileType})',filetypes=[('二进制文件',f'*.{fileType}')],initialfile=f'{self.cName}_lv.{self.lev}_{additionalTag}.{fileType}')
            if filePath=='':
                return False
            if filePath[-1-len(fileType):]!= f'.{fileType}':
                filePath += f'.{fileType}'
            filePath = filePath[:-1-len(fileType)]  +filePath[-1-len(fileType):]#+ f'-{additionalTag}'
            with open(filePath,'wb') as f:
                f.write(self.globalCharacBlobs[tabName])
            print(f'文件已保存{filePath}')

        def load_blob(fileType='blob'):
            #print('load')
            filePath = askopenfilename(filetypes=[(f'DNF {tabName} file',f'*.{fileType}')])
            if filePath=='':
                return False
            p = Path(filePath)
            if p.exists():
                with open(p,'rb') as f:
                    blob = f.read()
            self.globalCharacBlobs[tabName] = blob
            self.importFlgDict[tabName] = True

            #clear_item_Edit_Frame()
            #refill_Tree_View()
            taskID=len(self.loadPkgTaskList)
            self.loadPkgTaskList.append((taskID,tabName))
            self.fill_tab_treeviews(taskID=taskID)

        def changeItemSlotType(e=None):
            '''点击修改物品类别或点击新物品时，修改控件可编辑状态'''
            typeZh = typeEntry.get().split('-')[1]
            #print(typeZh)
            if typeZh in ['装备','宠物装备'] or cacheM.config.get('TYPE_CHANGE_ENABLE') == 1:
                numGradeLabel.config(text='品级：')
                configFrame(equipmentExFrame,'normal')
                configFrame(itemEditFrame.itemBasicInfoFrame,'normal')
                for widget in equipmentExFrame.children:
                    #print(widget)
                    try:
                        equipmentExFrame.children[widget].config(state='normal')
                    except:
                        pass

                forth.config(state='normal')

                for magicSealIDEntry in magicSealIDEntrys:
                    magicSealIDEntry.config(state='readonly')
                orbTypeEntry.config(state='readonly')
                orbValueEntry.config(state='readonly')
            else:
                configFrame(equipmentExFrame,'disabled')
                for widget in itemEditFrame.itemBasicInfoFrame.children:
                    try:
                        itemEditFrame.itemBasicInfoFrame.children[widget].config(state='disable')
                    except:
                        pass

                numGradeLabel.config(state='normal',text='数量：')
                numEntry.config(state='normal')
                itemIDEntry.config(state='normal')
                itemNameEntry.config(state='normal')
                delBtn.config(state='normal')
                resetBtn.config(state='normal')
                typeEntry.config(state='normal')
                enableTestBtn.config(state='normal')
            if typeEntry.get().split('-')[0]=='0':
                typeEntry.config(state='normal')
            else:
                typeEntry.config(state='normal' if cacheM.config.get('TYPE_CHANGE_ENABLE') == 1 else 'disable')
        
        def clear_item_Edit_Frame(clearTitle=True):
            '''清空右侧编辑槽'''
            #if clearTitle:
            #    itemSlotEditFrame.config(text=f'物品信息编辑')
            itemEditFrame.currentEditLabelVar.set(f'(0)')
            itemIDEntry.delete(0,tk.END)
            itemNameEntry.delete(0,tk.END)
            numEntry.delete(0,tk.END)
            durabilityEntry.delete(0,tk.END)
            itemEditFrame.sealCountE.delete(0,tk.END)
            EnhanceEntry.delete(0,tk.END)
            IncreaseEntry.delete(0,tk.END)
            IncreaseTypeEntry.delete(0,tk.END)
            forgingEntry.delete(0,tk.END)
            otherworldEntry.delete(0,tk.END)
            orbEntry.delete(0,tk.END)
            orbTypeEntry.set('')
            orbValueEntry.set('')
            itemSlotBytesE.delete(0,tk.END)
            
            for magicSealIDEntry in magicSealIDEntrys:
                magicSealIDEntry.config(state='normal')
            
            
            
            for magicSealIDEntry in magicSealIDEntrys:
                magicSealIDEntry.delete(0,tk.END)
            for magicSealEntry in magicSealEntrys:
                magicSealEntry.set('')
            for magicSealLevelEntry in magicSealLevelEntrys:
                magicSealLevelEntry.delete(0,tk.END)

            for magicSealIDEntry in magicSealIDEntrys:
                magicSealIDEntry.config(state='readonly')

        def fillItemEditFrame(itemSlot:sqlM.DnfItemSlot):
            '''传入slot对象，更新右侧编辑槽，不触发保存'''
            configFrame(itemEditFrame.itemEditFrame,'normal')

            clear_item_Edit_Frame(False)


            itemSealVar.set(itemSlot.isSeal)
            itemIDEntry.insert(0,itemSlot.id)
            durabilityEntry.insert(0,itemSlot.durability)
            try:
                itemNameEntry.insert(0,str(cacheM.ITEMS_dict.get(itemSlot.id)))
            except:
                itemNameNew = ''
                for c in str(cacheM.ITEMS_dict.get(itemSlot.id)):
                    itemNameNew += c if ord(c) < 0xffff else ''
                    cacheM.ITEMS_dict[itemSlot.id] = itemNameNew
                itemNameEntry.insert(0,itemNameNew)
            itemEditFrame.sealCountE.delete(0,tk.END)
            itemEditFrame.sealCountE.insert(0,itemSlot.sealCnt)
            numEntry.insert(0,itemSlot.num_grade)
            EnhanceEntry.insert(0,itemSlot.enhancementLevel)
            forgingEntry.insert(0,itemSlot.forgeLevel)
            otherworldEntry.insert(0,itemSlot.otherworld.hex())
            orbEntry.insert(0,itemSlot.orb)
            enhance:dict = cacheM.cardDict_zh.get(itemSlot.orb)
            if enhance is not None:
                try:
                    enhanceType,value = enhance.copy().popitem()
                    orbTypeEntry.set(enhanceType)
                    setOrbTypeCom(1)
                    orbValueEntry.set(value)
                except:
                    print(f'宝珠加载失败，{itemSlot.orb}')
                    pass
            coverMagic,magicSeals = itemSlot.readMagicSeal()
            itemSlotBytesE.insert(0,itemSlot.build_bytes().hex())

            for i in range(4):
                magicSealEntrys[i].set(magicSeals[i][1])
                magicSealIDEntrys[i].config(state='normal')
                magicSealIDEntrys[i].insert(0,magicSeals[i][0])
                magicSealIDEntrys[i].config(state='readonly')
                magicSealLevelEntrys[i].insert(0,magicSeals[i][2])
                

            IncreaseEntry.insert(0,itemSlot.increaseValue)

            IncreaseTypeEntry.set(itemSlot.increaseTypeZh)


            typeEntry.set(str(itemSlot.type)+'-'+itemSlot.typeZh)
            if coverMagic % 4 == 3:
                forthSealEnable.set(1)
            else:
                forthSealEnable.set(0)
            

            changeItemSlotType()
            if itemSlot.id == 0:
                typeEntry.config(state='readonly')
            
        @inThread
        def set_inv_capacity(event=None):
            capacity = int(itemEditFrame.inv_capacityE.get())
            sql = f'update inventory set inventory_capacity={capacity} where charac_no={self.cNo}'
            sqlM.execute_commit('taiwan_cain_2nd',sql)
            self.inventory_capacity = capacity
            self.checkBloblegal()
            set_treeview_color()
            print(f'修改背包容量为{capacity}')

        def getItemPVFInfo()->str:
            try:
                itemID = int(itemIDEntry.get())
            except:
                return None
            res = cacheM.get_Item_Info_In_Text(itemID).replace(r'%%',r'%').strip()
            return res
        
        def delete_all_item():
            '''删除所有物品'''
            if not messagebox.askokcancel('删除确认',f'确定删除{tabName}所有物品？\n请确认账号不在线或正在使用其他角色\n'):
                return False
            setDelete()
            CharacItemsDict = self.selectedCharacItemsDict[tabName]
            editedDict = {i:sqlM.DnfItemSlot() for i in CharacItemsDict.keys()}
            self.editedItemsDict[tabName] = editedDict
            sqlM.commit_change_blob(self.globalCharacBlobs[tabName],editedDict,self.cNo,globalBlobs_map[tabName])
            self.selectCharac_()
            print(f'====清空成功==== {tabName} 角色ID：{self.cNo}')
            
        def set_treeview_color():
            if self.importFlgDict.get(tabName) is not None:
                initTag = 'edited'
            else:
                initTag = ''
            for i_name in itemsTreev_now.get_children():
                try:
                    index,name,num,id_,*_ = itemsTreev_now.item(i_name)['values']
                    tag = initTag
                    if len(cacheM.PVFcacheDict.keys())!=0:
                        if index in self.errorItemsListDict[tabName]:
                            tag = 'error'
                        elif index in self.unknowItemsListDict[tabName]:
                            tag = 'unknow'
                    itemSlot:sqlM.DnfItemSlot = self.editedItemsDict.get(tabName).get(index)
                    if itemSlot  is not None:
                        if itemSlot.id == 0:
                            tag = 'deleted'
                        else:
                            tag = 'edited'
                    itemsTreev_now.item(i_name,tags=tag)
                except:
                    pass

        def editSave(retType='bool'):
            '''保存编辑信息'''
            
            if self.currentItemDict.get(tabName) is None:#没有加载角色数据
                if retType == 'bool':
                    return False
                else:
                    return b'\x00'*61
            #try:
            index,itemSlot_,*_ = self.currentItemDict.get(tabName)
            itemSlot:sqlM.DnfItemSlot = deepcopy(itemSlot_)
            itemSlot.id = int(itemIDEntry.get())
            itemSlot.isSeal = itemSealVar.get()
            itemSlot.num_grade = int(numEntry.get())
            itemSlot.durability = int(durabilityEntry.get())
            itemSlot.sealCnt = int(itemEditFrame.sealCountE.get())
            itemSlot.enhancementLevel= int(EnhanceEntry.get())
            itemSlot.forgeLevel = int(forgingEntry.get())
            itemSlot.increaseType = int(IncreaseTypeEntry.get().split('-')[-1])
            itemSlot.increaseValue = int(IncreaseEntry.get())
            itemSlot.type = int(typeEntry.get().split('-')[0])
            #if enableTestVar.get() == 1:
            orb = int(orbEntry.get().replace(' ',''))
            itemSlot.orb = orb
            otherworld = str2bytes(otherworldEntry.get().replace(' ',''))
            if len(itemSlot.otherworld)==len(otherworld):
                itemSlot.otherworld = otherworld
            magicSeals = []
            for i in range(4):
                magicSeals.append([int(magicSealIDEntrys[i].get()),magicSealEntrys[i].get(),int(magicSealLevelEntrys[i].get())])
            if forthSealEnable.get()==1:
                coverMagic = 3  
            elif itemSlot.coverMagic==3:
                coverMagic = 0
            else:
                coverMagic = itemSlot.coverMagic
            
            itemSlot.coverMagic = coverMagic
            magicSeal = itemSlot.buildMagicSeal([coverMagic,magicSeals])

            if len(itemSlot.magicSeal)==len(magicSeal):
                itemSlot.magicSeal = magicSeal
            slotBytes = itemSlot.build_bytes()
            itemSlot.oriBytes = slotBytes
            #print(slotBytes)
            #print(self.selectedCharacItemsDict[tabName][index].oriBytes)
            if retType=='bool':
                if slotBytes!= self.selectedCharacItemsDict[tabName][index].oriBytes:
                    
                    if itemSlot.id!=0 and itemSlot.type==0:
                        messagebox.askokcancel('物品状态确认','当前物品种类为空！请清空格子或设置合适种类以继续保存。')
                        #enableTypeChangeVar.set(1)
                        typeEntry.config(state='readonly')
                        return 'TypeEmptyFalse'
                    if '时装' in cacheM.getStackableTypeMainIdAndZh(itemSlot.id):
                        messagebox.askokcancel('物品状态确认','当前物品种类为时装！时装无法保存至物品栏')
                        return 'AvatarItemFalse'
                    self.editedItemsDict[tabName][index] = itemSlot
                    return True
                else:
                    if index in self.editedItemsDict[tabName].keys():
                        self.editedItemsDict[tabName].pop(index)
                    return False
            else:
                return slotBytes
        
        def update_Treeview():
            '''更新treeview名称'''
            editedDict = self.editedItemsDict[tabName]
            characItemsDict = self.selectedCharacItemsDict[tabName]
            for item in itemsTreev_now.get_children():
                values = itemsTreev_now.item(item)['values']
                index = values[0]
                if editedDict.get(index) is not None:
                    dnfItemSlot:sqlM.DnfItemSlot = editedDict.get(index)
                elif characItemsDict.get(index) is not None:
                    dnfItemSlot:sqlM.DnfItemSlot = characItemsDict.get(index)
                else:
                    continue
                name = str(cacheM.ITEMS_dict.get(dnfItemSlot.id))
                if dnfItemSlot.typeZh in ['装备'] and dnfItemSlot.enhancementLevel>0:
                    name = f'+{dnfItemSlot.enhancementLevel} ' + name
                #if dnfItemSlot.typeZh in ['消耗品','材料','任务材料','宠物消耗品','副职业']:
                num = dnfItemSlot.num_grade
                if dnfItemSlot.typeZh in ['装备']:
                    num = 1
                rarity = cacheM.get_Item_Info_In_Dict(dnfItemSlot.id).get('[rarity]')
                if rarity is not None:
                    rarity = f'[{rarity[0]}]-{rarityMap.get(rarity[0])}'
                values_unpack = [index,name,num,dnfItemSlot.id,rarity]
                itemsTreev_now.item(item,values=values_unpack)
            set_treeview_color()
            
        def showSelectedItemInfo(save=True,reset=False):
            '''显示当前选中物品槽，save:保存当前物品编辑状态，reset：重置当前编辑槽，而不是显示选中的槽'''
            if save:    
                saveState = editSave()
                if self.currentItemDict.get(tabName) is not None and saveState==True:
                    print('物品被编辑保存',self.editedItemsDict)
                elif saveState=='TypeEmptyFalse':
                    return False
                elif saveState=='AvatarItemFalse':
                    return False
            if reset:
                try:
                    index = int(itemEditFrame.currentEditLabelVar.get().split('(')[-1].replace(')',''))
                    #print(index)
                except:
                    return False
            else:
                sels = itemsTreev_now.selection()
                if len(sels)==0:#未选中任何物品
                    return True
                values = itemsTreev_now.item(itemsTreev_now.selection()[0])['values']  #数据库index
                index = values[0]
                
                update_Treeview()
            if self.editedItemsDict.get(tabName).get(index) is not None and not reset:#save and 
                itemSlot:sqlM.DnfItemSlot = self.editedItemsDict.get(tabName).get(index)
            else:
                itemSlot:sqlM.DnfItemSlot = self.selectedCharacItemsDict[tabName][index]
            fillItemEditFrame(itemSlot)
            log(f'{tabName}-{index}-{itemSlot}')
            print(itemSlot)
            self.currentItemDict[tabName] = [index,itemSlot,itemsTreev_now.focus()]
            #itemSlotEditFrame.config(text=f'物品信息编辑({index})')
            itemEditFrame.currentEditLabelVar.set(f'({index})')
            if len(cacheM.PVFcacheDict.keys())!=0 and self.errorInfoDict.get(tabName) is not None:
                errorInfo = self.errorInfoDict[tabName].get(index)
                if errorInfo is not None:
                    CreateOnceToolTip(itemsTreev_now,text=errorInfo)
            return True
        
        def searchItem(e:tk.Event):
            '''搜索物品名'''
            if e.x<100:return
            key = itemNameEntry.get()
            if len(key)>0:
                res = cacheM.searchItem(key)
                itemNameEntry.config(values=[item[1]+' '+ str([item[0]]) for item in res])
        def searchMagicSeal(com:ttk.Combobox):
            '''输入魔法封印时搜索'''
            key = com.get()
            res = cacheM.searchMagicSeal(key)
            res.sort()
            if key!='':
                res_ = list(cacheM.magicSealDict.items())
                res_.sort()
                res += res_
            #print(res)
            com.config(values=[item[1].strip()+' '+str([item[0]]) for item in res])
        
        def setMagicSeal(sealNameEntry,sealIDEntry):
            '''选择魔法封印属性时自动填充'''
            name = sealNameEntry.get()
            sealIDEntry.config(state='normal')
            sealIDEntry.delete(0,tk.END)
            sealIDEntry.insert(0,name.split(' [')[1].replace(']',''))
            sealIDEntry.config(state='readonly')
            sealNameEntry.set(name.split(' ')[0])

        def readSlotName(name_id='id'):
            if name_id=='id':
                id_ = itemIDEntry.get()
                try:
                    id_ = int(id_)
                except:
                    id_ = 0
                name = str(cacheM.ITEMS_dict.get(int(id_)))
            else:
                name,id_ = itemNameEntry.get().rsplit(' ',1)
                id_ = id_[1:-1]
                
            itemIDEntry.delete(0,tk.END)
            itemIDEntry.insert(0,id_)
            itemNameEntry.delete(0,tk.END)
            itemNameEntry.insert(0,name)
            itemNameEntry.config(values=[])
            #print(name,id_)

        def reset():
            showSelectedItemInfo(save=False,reset=True)

        def setDelete():
            itemSlot = sqlM.DnfItemSlot(b'')
            fillItemEditFrame(itemSlot)

        

        def refill_Tree_View(e=tk.Event):
            try:
                typeSel = int(typeBox.get().split('-')[0],16)
            except:
                typeSel = 0xff
            itemsTreev_now.delete(*itemsTreev_now.get_children())
            cacheM.ITEMS_dict[0] = ''
            CharacItemsDict = self.selectedCharacItemsDict[tabName]
            for index, dnfItemSlot in CharacItemsDict.items():
                    name = str(cacheM.ITEMS_dict.get(dnfItemSlot.id))
                    if tabName=='物品栏' and index in [0,1,2]:
                        #过滤物品栏前三个。这三个功能未知，会闪退
                        continue
                    if typeSel!=0xff and typeSel!=0x00: #过滤种类
                        if dnfItemSlot.id != 0 and dnfItemSlot.type != typeSel:
                            continue
                        if tabName in ['物品栏','宠物栏']:   #物品栏、宠物栏专属过滤
                            position = self.positionDict[typeSel][1]
                            if index not in range(*position) and index not in range(3,9):
                                #不是该位置的index，也不是快捷栏
                                continue
                            if index in range(3,9) and dnfItemSlot.id == 0:
                                #是，但是 id为0
                                continue
                    if typeSel==0x00:   #选择空位，过滤非空
                        emptySlotVar.set(1)
                        if dnfItemSlot.id != 0:
                            continue
                    if emptySlotVar.get()==0 and dnfItemSlot.id==0: #不显示空位，过滤空位
                        continue

                    if dnfItemSlot.typeZh in ['装备'] and dnfItemSlot.enhancementLevel>0:
                        name = f'+{dnfItemSlot.enhancementLevel} ' + name
                    #if dnfItemSlot.typeZh in ['消耗品','材料','任务材料','宠物消耗品','副职业']:
                    num = dnfItemSlot.num_grade
                    if dnfItemSlot.typeZh in ['装备']:
                        num = 1
                    rarity = cacheM.get_Item_Info_In_Dict(dnfItemSlot.id).get('[rarity]')
                    if rarity is not None:
                        rarity = f'[{rarity[0]}]-{rarityMap.get(rarity[0])}'
                    values_unpack = [index,name,num,dnfItemSlot.id,rarity]
                    try:
                        itemsTreev_now.insert('',tk.END,values=values_unpack)
                    except:
                        name_new = ''
                        for c in name:
                            name_new += c if ord(c)<0xffff else ''

                        values_unpack = [index,name_new,num,dnfItemSlot.id]
                        itemsTreev_now.insert('',tk.END,values=values_unpack)

                    CharacItemsDict[index] = dnfItemSlot
            set_treeview_color()
            self.w.after(1000,set_treeview_color)   #延迟1s再次检查，等待物品栏分析结果
        
        self.fillTreeFunctions[tabName] = refill_Tree_View
        self.editedItemsDict[tabName] = {}  #存储每个标签页正在编辑的物品
        self.itemInfoClrFuncs[tabName] = clear_item_Edit_Frame
        self.editFrameUpdateFuncs[tabName] = fillItemEditFrame
        self.tabNames.append(tabName)
        
        if tabName!='物品栏':
            itemEditFrame.inv_capacityE.destroy()
            itemEditFrame.inv_capacityL.destroy()
        else:
            itemEditFrame.inv_capacityE.bind('<<ComboboxSelected>>',set_inv_capacity)
            self.invCapacityE = itemEditFrame.inv_capacityE
        inventoryFrame = itemEditFrame
        inventoryFrame.pack(expand=True)

        invBowserFrame = itemEditFrame.invBowserFrame


        emptySlotVar = itemEditFrame.emptySlotVar
        emptySlotVar.set(0)
        itemEditFrame.showEmptyBtn.config(command=refill_Tree_View)

        values = [f'0x{"%02x" % item[0]}-{item[1]}' for item in sqlM.DnfItemSlot.typeDict.items()] +['0xff-全部']
        typeBox = itemEditFrame.typeBoxE
        typeBox.config(values=values,state='readonly') 
        typeBox.set('0xff-全部')
        typeBox.bind('<<ComboboxSelected>>',refill_Tree_View)         

            
            

        itemsTreev_now = itemEditFrame.itemsTreev_now
        itemsTreev_now.pack(side=tk.LEFT,fill='both',expand=True)

        itemsTreev_now.tag_configure('edited', background='lightblue')
        itemsTreev_now.tag_configure('deleted', background='gray')
        itemsTreev_now.tag_configure('error', background='red')
        itemsTreev_now.tag_configure('unknow', background='yellow')
        self.itemsTreevs_now[tabName] = itemsTreev_now
        sbar1= itemEditFrame.itemsTreev_bar

        sbar1.config(command =itemsTreev_now.yview)
        itemsTreev_now.config(yscrollcommand=sbar1.set,xscrollcommand=sbar1.set)
        itemsTreev_now.bind('<<TreeviewSelect>>',lambda e:showSelectedItemInfo())
        self.currentTreeViews[tabName] = itemsTreev_now
        self.editFrameShowFuncs[tabName] = showSelectedItemInfo

        itemEditFrame.clearBtn.config(command=delete_all_item)
        exportBtn = itemEditFrame.exportBtn
        exportBtn.config(command=lambda:save_blob(globalBlobs_map[tabName]))
        CreateToolTip(exportBtn,text='保存当前数据到文件')
        importBtn = itemEditFrame.importBtn
        importBtn.config(command=lambda:load_blob(globalBlobs_map[tabName]))
        CreateToolTip(importBtn,text='从文件导入数据并覆盖')

        itemSlotEditFrame = itemEditFrame.itemEditFrame
        itemSealVar = itemEditFrame.itemSealVar
        itemSealBtn = itemEditFrame.itemSealBtn
        CreateToolTip(itemSealBtn,'无法封装的物品勾选会炸角色')
        itemNameEntry = itemEditFrame.itemNameEntry
        itemNameEntry.bind("<<ComboboxSelected>>",lambda e:readSlotName('name'))
        itemNameEntry.bind('<Button-1>',searchItem)
        CreateToolTip(itemNameEntry,textFunc=getItemPVFInfo)
        itemIDEntry = itemEditFrame.itemIDEntry
        itemIDEntry.bind('<FocusOut>',lambda e:readSlotName('id'))
        itemIDEntry.bind('<Return>',lambda e:readSlotName('id'))
        # 3

        numGradeLabel = itemEditFrame.numGradeLabel
        numEntry = itemEditFrame.numEntry
        numEntry.config(from_=0, to=4294967295)
        CreateToolTip(numEntry,'当为装备时，表示为品级\n数值与品级关系较为随机\n(0~4,294,967,295)')
        durabilityEntry = itemEditFrame.durabilityEntry

        # 4
        IncreaseTypeEntry = itemEditFrame.IncreaseTypeEntry
        IncreaseTypeEntry.config(values=['空-0','异次元体力-1','异次元精神-2','异次元力量-3','异次元智力-4'])
        IncreaseEntry = itemEditFrame.IncreaseEntry
        IncreaseEntry.config(from_=0, to=65535)

        # 5
        EnhanceEntry = itemEditFrame.EnhanceEntry
        EnhanceEntry.config(from_=0, to=31)
        delBtn = itemEditFrame.delBtn
        delBtn.config(command=setDelete)
        CreateToolTip(delBtn,'标记当前物品为待删除物品')
        # 6
        row = 6
        forgingEntry = itemEditFrame.forgingEntry
        forgingEntry.config(from_=0, to=31)
        resetBtn = itemEditFrame.resetBtn
        resetBtn.config(command=reset)
        # 7 
        def enableTypeChange():
            #print(itemEditFrame.enableTypeChangeVar.get())
            typeEntry.config(state='readonly' if itemEditFrame.enableTypeChangeVar.get() == 1 else 'disable')

        #itemEditFrame.enableTestFrame = enableTestFrame
        enableTestBtn = itemEditFrame.enableTypeBtn
        enableTestBtn.config(command=enableTypeChange)
        row = 7

        typeEntry = itemEditFrame.typeEntry
        typeEntry.config(state='readonly',values=['1-装备','2-消耗品','3-材料','4-任务材料','5-宠物','6-宠物装备','7-宠物消耗品','10-副职业'])
        typeEntry.bind('<<ComboboxSelected>>',changeItemSlotType)
        tip = '物品栏仅3-8可随意修改类型，否则炸角色\n'
        tip += '快捷栏：3 - 8\n' +\
            '装备栏：9 - 56\n' +\
            '消耗品：57 - 104\n' +\
            '材   料：105 - 152\n' +\
            '任务材料：153 - 200\n' +\
            '副职业：201 - 248\n' +\
            '宠物装备：0-48, 99-101\n' +\
            '宠物消耗品：49-97'

    
        CreateToolTip(typeEntry,tip)
        # 8 
        equipmentExFrame = itemEditFrame.equipmentExFrame
        # 8-1
        otherworldEntry = itemEditFrame.otherworldEntry
        # 8-2
        def setOrbTypeCom(e:tk.Event):
            enhanceKeyZh = orbTypeEntry.get()
            enhanceItems = cacheM.enhanceDict_zh.get(enhanceKeyZh)
            enhanceItemsList = list(enhanceItems.items())
            #print(items)
            try:
                enhanceItemsList.sort(key=lambda x:x[1][0],reverse=True)
            except:
                pass
            items_str = []
            for item in enhanceItemsList:
                if isinstance(item,list):
                    item_str = '|'.join([str(value) for value in item[1]]) +' '*20 +f'-{item[0]}'
                else:
                    item_str = str(item[1]) + ' '*20 +f'-{item[0]}'
                items_str.append(item_str)
            orbValueEntry.config(values=items_str)    
            orbValueEntry.set(f'属性值({len(items_str)})')
        
        def setOrbValueCom(e:tk.Event):
            itemID = orbValueEntry.get().split('-')[-1]
            orbEntry.delete(0,tk.END)
            orbEntry.insert(0,itemID)
            
        row = 2

        orbTypeEntry = itemEditFrame.orbTypeEntry
        orbValueEntry = itemEditFrame.orbValueEntry
        orbEntry = itemEditFrame.orbEntry
        orbTypeEntry.bind('<<ComboboxSelected>>',setOrbTypeCom)
        orbValueEntry.bind('<<ComboboxSelected>>',setOrbValueCom)
        self.orbTypeEList.append(orbTypeEntry)
        def showOrb(e=tk.Event):
            try:
                return cacheM.get_Item_Info_In_Text(int(orbEntry.get())) if int(orbEntry.get())!=0 else ''
            except:
                return ''
        
        def changeOrbByID(e):
            try:
                enhance:dict = cacheM.cardDict_zh.get(int(orbEntry.get()))
                if enhance is not None:
                    enhanceType,value = enhance.copy().popitem()
                    orbTypeEntry.set(enhanceType)
                    setOrbTypeCom(1)
                    orbValueEntry.set(value)
            except:
                pass
        orbEntry.bind('<FocusOut>',changeOrbByID)
        orbEntry.bind('<Return>',changeOrbByID)
        CreateToolTip(orbEntry,textFunc=showOrb)
        # 8-3

        forthSealEnable = itemEditFrame.forthSealEnable
        forth = itemEditFrame.forth
        CreateToolTip(forth,'启用后无法使用游戏内魔法封印相关修改操作')
    
        magicSealEntrys = [itemEditFrame.magicSealEntry,itemEditFrame.magicSealEntry1,itemEditFrame.magicSealEntry2,itemEditFrame.magicSealEntry3]
        magicSealIDEntrys = [itemEditFrame.magicSealIDEntry,itemEditFrame.magicSealIDEntry1,itemEditFrame.magicSealIDEntry2,itemEditFrame.magicSealIDEntry3]
        magicSealLevelEntrys = [itemEditFrame.magicSealLevelEntry,itemEditFrame.magicSealLevelEntry1,itemEditFrame.magicSealLevelEntry2,itemEditFrame.magicSealLevelEntry3]

        def build_magic_view(i):
            magicSealEntry = magicSealEntrys[i]
            magicSealIDEntry = magicSealIDEntrys[i]
            magicSealLevelEntry = magicSealLevelEntrys[i]
            magicSealEntry.config(values=list(cacheM.magicSealDict.values()))
            magicSealIDEntry.config(state='readonly')
           #magicSealLevelEntry.config(from_=0,to=65535)
            
            magicSealEntry.bind('<Button-1>',lambda e:searchMagicSeal(magicSealEntry))
            magicSealEntry.bind('<<ComboboxSelected>>',lambda e:setMagicSeal(magicSealEntry,magicSealIDEntry))

            CreateToolTip(magicSealLevelEntry,'词条数值，0-65535')
            self.updateMagicSealFuncs[tabName+str(row)] = lambda: magicSealEntry.config(values=list(cacheM.magicSealDict.values()))

        for i in range(4):
            build_magic_view(i)
                
        if True:
            itemSlotBytesE = itemEditFrame.itemSlotBytesE
            CreateToolTip(itemSlotBytesE,textFunc=lambda:'物品字节数据：'+itemSlotBytesE.get())
            def genBytes():
                slotBytes = editSave('bytes')
                itemSlotBytesE.delete(0,tk.END)
                itemSlotBytesE.insert(0,slotBytes.hex())
            genBytesBtn = itemEditFrame.genBytesBtn
            genBytesBtn.config(command=genBytes)
            CreateToolTip(genBytesBtn,'根据物品槽数据编辑结果生成字节')

            def readBytes():
                itemBytes = str2bytes(itemSlotBytesE.get())
                fillItemEditFrame(sqlM.DnfItemSlot(itemBytes))
            importBtn = itemEditFrame.importBytesBtn
            importBtn.config(command=readBytes)
            CreateToolTip(importBtn,'读取字节，导入到编辑框\n用于物品复制')
            commitBtn = itemEditFrame.commitBtn
            commitBtn.config(command=ask_commit)
            CreateToolTip(commitBtn,f'提交当前[{tabName}]页面的所有修改')

