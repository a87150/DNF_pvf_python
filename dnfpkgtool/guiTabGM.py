'''GM 工具与气泡页签（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppTabGM:
    def _buildtab_GM(self):
        PVPMap_tmp = [f'{i}级' for i in range(1,11)]
        PVPMap_tmp.reverse()
        PVPMap_tmp2 = [f'{i}段' for i in range(1,11)]
        PVPMap_tmp3 = [f'至尊{i}' for i in range(1,11)]
        PVPMap_tmp4 = ['达人','名人','小霸王','霸王','斗神']
        PVPRankList = PVPMap_tmp+PVPMap_tmp2+PVPMap_tmp3+PVPMap_tmp4

        self.get_group_account_characs = lambda:...
        self.get_group_all_characs = lambda:...
        self.get_group_all_uids = lambda:...
        self.delete_mail_group = lambda:...
        self.localEventList = None
        self.blobCommitExFunc = lambda cNo=0:...
        self.updateFuncList = []
        self.eventList = []


        def update_Info():
            for func in self.updateFuncList:
                func()
        self.update_GM = update_Info
        def buildTab_usual():
            def charge(type='cera'):
                if not messagebox.askokcancel('充值确认',f'确定充值？\n将充值到当前角色[{self.cNo}][{self.cName}]'):
                    return False
                #update_cera_and_SP()
                type = ceraTypeE.get()
                value = int(ceraValueE.get())
                if type =='点券':
                    oldValue = cNoInfoDict['cera']
                    #sqlM.set_cera(self.uid,value+cNoInfoDict['cera'],'cera')
                    sqlM.charge_crea(self.uid,value,'cera')
                elif type =='代币':
                    oldValue = cNoInfoDict['cera_point']
                    #sqlM.set_cera(self.uid,value+cNoInfoDict['cera_point'],'cera_point')
                    sqlM.charge_crea(self.uid,value,'cera_point')
                elif type=='SP':
                    oldValue = cNoInfoDict['sp']
                    sqlM.charge_sp(self.cNo,value,'remain_sp')
                    #sqlM.set_skill_sp(self.cNo,value+cNoInfoDict['sp'],value+cNoInfoDict['sp2'],cNoInfoDict['tp'],cNoInfoDict['tp2'])
                elif type=='TP':
                    oldValue = cNoInfoDict['tp']
                    sqlM.charge_sp(self.cNo,value,'remain_sfp_1st')
                    #sqlM.set_skill_sp(self.cNo,cNoInfoDict['sp'],cNoInfoDict['sp2'],value+cNoInfoDict['tp'],value+cNoInfoDict['tp2'])
                elif type=='QP':
                    oldValue = cNoInfoDict['qp']
                    sqlM.charge_quest_point(self.cNo,value)
                    #sqlM.set_quest_point(self.cNo,value+cNoInfoDict['qp'])
                update_Info()
                print(f'角色[{self.cNo}][{self.cName}]-[{type}]充值完成 [{oldValue}]->[{oldValue+value}]')
                self.blobCommitExFunc(self.cNo)
            

            def clear_cera():
                update_cera_and_SP()
                type = ceraTypeE.get()
                if type =='点券':
                    sqlM.set_cera(self.uid,0,'cera')
                elif type =='代币':
                    sqlM.set_cera(self.uid,0,'cera_point')
                elif type=='SP':
                    sqlM.set_skill_sp(self.cNo,0,0,cNoInfoDict['tp'],cNoInfoDict['tp2'])
                elif type=='TP':
                    sqlM.set_skill_sp(self.cNo,cNoInfoDict['sp'],cNoInfoDict['sp2'],0,0)
                elif type=='QP':
                    sqlM.set_quest_point(self.cNo,0)
                update_Info()
                print('清空成功！')
                self.blobCommitExFunc(self.cNo)
            def update_cera_and_SP():
                if 'uid' not in dir(self):
                    return False
                cera, cera_point = sqlM.get_cera(self.uid)
                cNoInfoDict['cera'] = cera
                cNoInfoDict['cera_point'] = cera_point

                sp,sp2,tp,tp2 = sqlM.get_skill_sp(self.cNo)
                cNoInfoDict['sp'] = sp
                cNoInfoDict['sp2'] = sp2
                cNoInfoDict['tp'] = tp
                cNoInfoDict['tp2'] = tp2
                qp = sqlM.get_quest_point(self.cNo)
                cNoInfoDict['qp'] = qp
                ceraSVar.set(cera)#f'{"%6d" % cera}' if cera<999999 else '100w+')
                ceraPointSVar.set(cera_point)#f'{"%6d" % cera_point}' if cera_point<999999 else '100w+')
                spVar.set(sp)#f'{"%6d" % sp}' if sp<999999 else '100w+')
                qpStr = f'{qp}'# if qp<999 else '1k+'
                tpStr = f'{tp}'# if tp<999 else '1k+'
                qpTpVar.set(qpStr+'/'+tpStr)

            
            self.updateFuncList.append(update_cera_and_SP)
            cNoInfoDict = {}
            readOnlyWidgets = []

            ceraSVar = self.ceraSVar
            ceraSVar.set('000000')
            ceraPointSVar = self.ceraPointSVar
            ceraPointSVar.set('000000')
            spVar = self.spVar
            spVar.set('000000')
            qpTpVar = self.qpTpVar
            qpTpVar.set('00/00')

            ceraValueE = self.ceraValueE
            ceraValueE.set(0)
            ceraTypeE = self.ceraTypeE
            ceraTypeE.set('点券')
            readOnlyWidgets.append(ceraTypeE)
            self.ceraChargeBtn.config(command=charge)
            self.ceraClearBtn.config(command=clear_cera)


            def update_PVP():
                if self.cNo==0:
                    return False
                pvp_grade,win,pvp_point,win_point = sqlM.get_PVP(self.cNo)
                PVPgradeE.set(f'{PVPRankList[pvp_grade]}')
                PVPwinNumE.delete(0,tk.END)
                PVPwinNumE.insert(0,win)
                PVPwinPointE.delete(0,tk.END)
                PVPwinPointE.insert(0,win_point)
            
            def set_PVP():
                if not messagebox.askyesno('确认提交','确认提交PVP信息？'):
                    return False
                pvp_grade = PVPRankList.index(PVPgradeE.get())
                win = int(PVPwinNumE.get())
                pvp_point = int(PVPwinPointE.get())
                win_point = pvp_point
                sqlM.set_PVP(self.cNo,pvp_grade,win,pvp_point,win_point)
                update_Info()
                print('PVP数据提交完成')
            
            
            self.updateFuncList.append(update_PVP)

            PVPgradeE = self.PVPgradeE
            PVPgradeE.config(values=[f'{name}' for i,name in enumerate(PVPRankList)])
            readOnlyWidgets.append(PVPgradeE)

            PVPwinNumE = self.PVPwinNumE

            PVPwinPointE = self.PVPwinPointE
            self.PVPCommitBtn.config(command=set_PVP)

            def unlock_dungeon():
                if not messagebox.askyesno('确认提交','确认解锁副本难度？'):
                    return False
                dungeonList = list(cacheM.dungeonDict.keys())
                
                if dungeonList!=[]:
                    dungeons = ''
                    for i in dungeonList:
                        dungeons += f'{i}|3,'
                    dungeons = dungeons[:-1]
                else:
                    dungeons = '1|3,2|3,3|3,4|3,5|3,6|3,7|3,8|3,9|3,11|3,12|3,13|3,14|3,15|3,16|1,17|3,21|3,22|3,23|3,24|3,25|3,26|3,27|3,31|3,32|3,33|3,34|3,35|3,36|3,37|3,40|3,41|2,42|3,43|3,44|3,45|3,50|3,51|3,52|3,53|3,60|3,61|3,62|2,63|3,64|3,65|3,67|3,70|3,71|3,72|3,73|3,74|3,75|3,76|3,77|3,80|3,81|3,82|3,83|3,84|3,85|3,86|3,87|3,88|3,89|3,90|3,91|2,92|3,93|3,100|3,101|3,102|3,103|3,104|3,110|3,111|3,112|3,140|3,141|3,502|3,511|3,515|1,518|1,521|3,1000|3,1500|3,1501|3,1502|3,1507|1,3506|3,10000|3'
                #print(dungeons)
                sqlM.unlock_all_lev_dungeon(self.uid,dungeons)
                print('解锁副本难度指令执行完成')

            def reset_blood_dungeon():
                if not messagebox.askyesno('确认提交','确认重置祭坛与异界副本入场次数？'):
                    return False
                sqlM.reset_blood_dungeon(self.cNo)
                sqlM.reset_dimension(self.cNo)
                print('重置祭坛与异界次数指令执行完成')
            
            def unlock_ALL_Level_equip():
                if not messagebox.askyesno('确认提交','确认解锁装备等级限制？'):
                    return False
                sqlM.unlock_ALL_Level_equip(self.cNo)
                print('解锁装备等级限制指令执行完成')

            def enable_LR_slot():
                if not messagebox.askyesno('确认提交','确认解锁左右槽位？'):
                    return False
                sqlM.enable_LR_slot(self.cNo)
                print('解锁左右槽位指令执行完成')
            
            def maxmize_expert_lev():
                if not messagebox.askyesno('确认提交','确认提升副职业至满级？'):
                    return False
                sqlM.maxmize_expert_lev(self.cNo)
                print('提升副职业至满级指令执行完成')
            
            def unlock_register_limit():
                if not messagebox.askyesno('确认提交','确认解除账号限制？'):
                    return False
                sqlM.unlock_register_limit(self.uid)
                print('解除账号限制指令执行完成')

            unlockBtn = self.liftLimitBtn
            unlockBtn.config(command=unlock_register_limit)
            CreateToolTip(unlockBtn,'解除建号限制、限制交易、封号等账号异常状态')
            self.enableLRSlotBtn.config(command=enable_LR_slot)
            self.liftEquLevLimitBtn.config(command=unlock_ALL_Level_equip)
            self.enableAllLevDungeonBtn.config(command=unlock_dungeon)
            self.resetBloodDungeonBtn.config(command=reset_blood_dungeon)
            CreateToolTip(self.resetBloodDungeonBtn,'重置祭坛与异界副本入场次数')
            self.maxLevExpertBtn.config(command=maxmize_expert_lev)

        def build_Tab_Money():
            pkgMoneyE = self.pkgMoneyE
            pkgMoneyBtn = self.pkgMoneyBtn
            accountMoneyE = self.accountMoneyE
            accountMoneyBtn = self.accountMoneyBtn
            payCoinE = self.payCoinE
            payCoinBtn = self.payCoinBtn
            def get_money():
                if self.cNo==0:
                    return False
                money = sqlM.get_charac_money(self.cNo)
                pkgMoneyE.delete(0,tk.END)
                pkgMoneyE.insert(0,money)
                return money
            def set_money():
                if not messagebox.askokcancel('确认提交','确认提交金币修改？'):
                    return False
                if self.cNo==0:
                    return False
                money = int(pkgMoneyE.get())
                sqlM.set_charac_money(self.cNo,money)
                print(f'角色[{self.cNo}][{self.cName}]金币修改完成[{money}]，请手动重载数据')
            def get_account_money():
                if self.uid==0:
                    return False
                money = sqlM.get_account_money(self.uid)
                accountMoneyE.delete(0,tk.END)
                accountMoneyE.insert(0,money)
                return money
            def set_account_money():
                if not messagebox.askokcancel('确认提交','确认提交账号金币修改？'):
                    return False
                if self.uid==0:
                    return False
                money = int(accountMoneyE.get())
                sqlM.set_account_money(self.uid,money)
                print(f'账号[{self.uid}]金币修改完成[{money}]，请手动重载数据')
                #app.blobCommitExFunc(app.cNo)
            def get_pay_coin():
                if self.cNo==0:
                    return False
                paycoin = sqlM.get_pay_coin(self.cNo)
                payCoinE.delete(0,tk.END)
                payCoinE.insert(0,paycoin)
                return paycoin
            def set_pay_coin():
                if not messagebox.askokcancel('确认提交','确认提交复活币修改？'):
                    return False
                if self.cNo==0:
                    return False
                paycoin = int(payCoinE.get())
                sqlM.set_pay_coin(self.cNo,paycoin)
                print(f'角色[{self.cNo}][{self.cName}]复活币修改完成[{paycoin}]，请手动重载数据')
            
            self.updateFuncList.append(get_money)
            self.updateFuncList.append(get_account_money)
            self.updateFuncList.append(get_pay_coin)

            pkgMoneyBtn.config(command=set_money)
            accountMoneyBtn.config(command=set_account_money)
            payCoinBtn.config(command=set_pay_coin)

        def buildTab_mail():
            def searchItem(e):
                if e.x<100:return
                key = itemNameEntry.get()
                if len(key)>0:
                    res = cacheM.searchItem(key)
                    itemNameEntry.config(values=[item[1] +' '+ str([item[0]]) for item in res])
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
                itemID = int(id_)
                typeid,itemType = cacheM.getStackableTypeMainIdAndZh(itemID)
                
                #print(int(id_),name,typeid,itemType)
                typeEntry.set(str(typeid)+'-'+itemType)

                changeItemSlotType()         
            def getItemPVFInfo():
                try:
                    itemID = int(itemIDEntry.get())
                except:
                    return None
                res = cacheM.get_Item_Info_In_Text(itemID).replace(r'%%',r'%').strip()
                return res
            def changeItemSlotType():
                typeZh = typeEntry.get().split('-')[1] 
                if typeZh in ['装备','宠物','时装']:
                    numGradeLabel.config(text='品级：')
                    for widget in itemEditFrame.children.values():
                        try:
                            widget.config(state='normal')
                        except:
                            pass
                    if enduranceEntry.get()=='':
                        enduranceEntry.insert(0,0)
                    if numEntry.get()=='':
                        numEntry.insert(0,1)
                    if IncreaseTypeEntry.get()=='':
                        IncreaseTypeEntry.set('空-0')
                    if IncreaseEntry.get()=='':
                        IncreaseEntry.insert(0,'0')
                    if EnhanceEntry.get()=='':
                        EnhanceEntry.insert(0,'0')
                    if forgingEntry.get()=='':
                        forgingEntry.insert(0,'0')
                    
                else:
                    for widget in itemEditFrame.children.values():
                        try:
                            widget.config(state='disable')
                        except:
                            pass
                    numGradeLabel.config(state='normal',text='数量：')
                    numEntry.config(state='normal')
                    itemIDEntry.config(state='normal')
                    itemNameEntry.config(state='normal')
                    self.itemIDLabel.config(state='normal')
                    if numEntry.get()=='':
                        numEntry.insert(0,1)
                typeEntry.config(state='readonly')
                goldE.config(state='normal')
                goldLabel.config(state='normal')
            def get_Item_info()->list:
                id = itemIDEntry.get()
                seal = itemSealVar.get()
                num = numEntry.get()
                endurance = enduranceEntry.get()
                IncreaseType = IncreaseTypeEntry.get().split('-')[-1]
                IncreaseValue = IncreaseEntry.get()
                enhanceValue = EnhanceEntry.get()
                forgeLevel = forgingEntry.get()
                itemType = typeEntry.get().split('-')[-1]
                avatar_flag = 0
                creature_flag = 0
                if itemType=='宠物':
                    creature_flag = 1
                elif itemType=='时装':
                    avatar_flag = 1
                    endurance = 1
                    num = 773

                res = []
                for value in [id,seal,num,endurance,IncreaseType,IncreaseValue,enhanceValue,forgeLevel,creature_flag,avatar_flag]:
                    try:
                        res.append(int(value))
                    except:
                        res.append(0)
                return res
            def send_mail(cNo,confirm=False):
                if confirm:
                    if not messagebox.askokcancel('发送确认',f'确定发送邮件到当前角色[{self.cName}][{cNo}]？'):
                        return False
                if cNo==0:
                    messagebox.showerror('错误','请先选择角色')
                    return False
                gold = int(goldE.get())
                sender = senderE.get()
                message = messageE.get()
                letterID = sqlM.send_message(cNo,sender,message)
                messages = cacheM.config.get('MESSAGES',['欢迎使用GM功能，有运行错误请提交issue至GitHub'])
                if messages.index(message)!=0:
                    messages.remove(message)
                    messages.insert(0,message)
                    cacheM.save_config()
                messageE.config(values=messages)
                senders = cacheM.config.get('SENDERS',['背包编辑工具'])
                if senders.index(sender)!=0:
                    senders.remove(sender)
                    senders.insert(0,sender)
                    cacheM.save_config()
                senderE.config(values=senders)
                itemID,seal,num,endurance,IncreaseType,IncreaseValue,enhanceValue,forgeLevel,creature_flag,avatar_flag = get_Item_info()
                if itemID==0 and gold==0:
                    print(f'发送文本完成-{cNo}')
                    return True
                sqlM.send_postal(cNo,letterID,sender,message,itemID,IncreaseType,IncreaseValue,
                                forgeLevel,seal,num,enhanceValue,gold,avatar_flag,creature_flag,endurance)
                if cacheM.stackableDict.get(itemID) is None:
                    num = 1
                print(f'发送完成-角色[{cNo}]-物品[{cacheM.ITEMS_dict.get(itemID)}][{itemID}]-数量[{num}]-金币[{gold}]')
                self.blobCommitExFunc(cNo)
                letter_send_dict[letterID] = {
                    'cNo':cNo, 'itemID':itemID,'gold':gold,'num':num
                }
                if cNo==self.cNo:
                    self.selectCharac()
                
            def send_mail_all():
                characs = sqlM.get_all_charac()
                #print(characs)
                if not messagebox.askokcancel('发送确认',f'确定发送邮件到当前所有的{len(characs)}个角色？'):
                    return False
                i=1
                for uid,cNo,*_ in characs:
                    print(f'当前发送({i}/{len(characs)}/{characs[i-1]})')
                    send_mail(cNo)
                    i+=1
            def send_mail_VIP(all=False):
                if all==False:
                    characs = sqlM.get_VIP_charac()
                else:
                    characs = sqlM.get_VIP_charac(True)
                print(characs)
                if not messagebox.askokcancel('发送确认',f'确定发送邮件到当前VIP的{len(characs)}个角色？'):
                    return False
                i=1
                for uid,cNo,*_ in characs:
                    send_mail(cNo)
                    print(f'当前发送({i}/{len(characs)})')
                    i+=1
                print(f'发送完成({len(characs)})!')

            def send_mail_online():
                onlineCharacList = sqlM.get_online_charac()
                print(onlineCharacList)
                if not messagebox.askokcancel('发送确认',f'确定发送邮件到当前在线的{len(onlineCharacList)}个角色？'):
                    return False
                
                i=1
                for uid,cNo,*_ in onlineCharacList:
                    send_mail(cNo)
                    print(f'当前发送({i}/{len(onlineCharacList)})')
                    i+=1
                print(f'发送完成({len(onlineCharacList)})!')
            
            @inThread
            def clearAllMail():
                allPostalID = sqlM.get_all_postalID()
                if not runOnUi(messagebox.askokcancel,'发送确认',f'确定清空当前所有的{len(allPostalID)}封邮件？'):
                    return False
                i = 1
                for postalID in allPostalID:
                    sqlM.delete_mail_postal(postalID[0])
                    print(f'删除邮件{postalID} {i}/{len(allPostalID)}')
                    i+=1
                

            self.readSlotID = readSlotName
            itemEditFrame = self.itemEditFrame
            itemSealVar = self.itemSealVar
            itemSealVar.set(0)
            itemSealBtn = self.itemSealBtn
            CreateToolTip(itemSealBtn,'无法封装的物品勾选会炸角色')
            itemNameEntry = self.itemNameEntry
            itemNameEntry.bind('<Button-1>',searchItem)
            itemNameEntry.bind("<<ComboboxSelected>>",lambda e:readSlotName('name'))
            CreateToolTip(itemNameEntry,textFunc=getItemPVFInfo)
            itemIDEntry = self.itemIDEntry
            itemIDEntry.bind('<FocusOut>',lambda e:readSlotName('id'))
            itemIDEntry.bind('<Return>',lambda e:readSlotName('id'))
            self.mailItemIDEntry = itemIDEntry
            self.setMailItemIDFun = lambda :readSlotName('id')

            numGradeLabel = self.numGradeLabel

            numEntry = self.numEntry
            CreateToolTip(numEntry,'当为装备时，表示为品级\n数值与品级关系较为随机\n(1~4,294,967,295)\n填充0时会导致物品维修后消失')
            enduranceEntry = self.durabilityEntry
            IncreaseTypeEntry = self.IncreaseTypeEntry
            IncreaseTypeEntry.config(state='readonly',values=['空-0','异次元体力-1','异次元精神-2','异次元力量-3','异次元智力-4'])
            IncreaseEntry = self.IncreaseEntry
            
            EnhanceEntry = self.EnhanceEntry

            typeEntry = self.typeEntry
            typeEntry.config(state='readonly',values=['1-装备','2-消耗品','3-材料','4-任务材料','5-宠物','6-宠物装备','7-宠物消耗品','8-时装','10-副职业'])
            typeEntry.bind("<<ComboboxSelected>>",lambda e:changeItemSlotType())
            forgingEntry = self.forgingEntry
            goldLabel = self.goldLabel
            goldE = self.goldE
            goldE.insert(0,'0')
                
            senderE = self.senderE
            senders = cacheM.config.get('SENDERS',['背包编辑工具'])
            senderE.config(values=senders)
            senderE.set(senders[0])
            CreateToolTip(senderE,textFunc=lambda:'发件人：'+senderE.get())
            messageE = self.msgE
            messages = cacheM.config.get('MESSAGES',['欢迎使用GM功能，有运行错误请提交issue至GitHub'])
            messageE.config(values=messages)
            messageE.set(messages[0])
            #messageE.insert(0,'欢迎使用GM功能，有运行错误请提交issue至GitHub')
            CreateToolTip(messageE,textFunc=lambda:'邮件文本：'+messageE.get())

            if True:
                self.send2allBtn.config(command=send_mail_all)
                self.send2onlineBtn.config(command=send_mail_online)
                self.send2VIPaBtn.config(command=send_mail_VIP)
                self.send2VIPcBtn.config(command=lambda:send_mail_VIP(True))
                self.clearMailBtn.config(command=clearAllMail)
                self.send2currentBtn.config(command=lambda:send_mail(self.cNo,True))
        
        def buildTab_event():
            def get_available_event():
                eventList = sqlM.get_event_available()
                from zhconv import convert
                self.eventList = [[item[0],item[1],convert(item[2],'zh-cn')] for item in eventList]
                self.localEventList = None
                import json,pathlib
                EventPath = './config/eventList.json'
                if self.localEventList is None and pathlib.Path(EventPath).exists():
                    self.localEventList = loadJsonFile(EventPath)
                if self.localEventList!= self.eventList:
                    if str(self.eventList).count('?')<30:
                        with open(EventPath,'w',encoding='utf-8') as f:
                            json.dump(self.eventList,f,ensure_ascii=False)
                    elif  self.localEventList is not None:
                        self.eventList = self.localEventList
                eventList_new = [f'{item[0]}-{item[2]}' for item in self.eventList]
                #print(eventList)
                eventNameE.set(f'选择活动({len(eventList_new)})')
                eventNameE.config(values=eventList_new)
            
            def get_running_event():
                eventList = sqlM.get_event_running()
                runningList = []
                for log_id,eventid,para1,para2 in eventList:
                    flg = False
                    for Eid,name,explain in self.eventList:
                        if eventid==Eid:
                            runningList.append([log_id,explain,para1,para2])
                            flg = True
                            break
                    if flg:continue
                    runningList.append([log_id,'explain',para1,para2])
                #print(eventList,runningList)
                for child in eventTreeNow.get_children():
                    eventTreeNow.delete(child)
                for item in runningList:
                    eventTreeNow.insert('',tk.END,values=item)
                return runningList
            update_event_list_func = lambda:[get_available_event(),get_running_event()]
            eventTreeNow = self.eventTreeNow
            eventTreeNow.tag_configure('deleted', background='gray')

            def del_event():
                try:
                    sel = eventTreeNow.item(eventTreeNow.focus())
                    print(sel['values'])
                    id = int(sel['values'][0])
                except:
                    print('未选中活动')
                    return False
                sqlM.del_event(id)
                update_event_list_func()
                print(f'活动已删除，请重启服务器')
            
            def set_event():
                try:
                    id = int(eventNameE.get().split('-')[0])
                    para1 = eventArg1E.get()
                    if para1=='':
                        para1 = 1
                    para2 = 0
                    sqlM.set_event(id,para1,para2)
                except:
                    print('活动添加失败')
                    return False
                print(f'活动已添加，请重启服务器')
                update_event_list_func()
            
            def select_new_event(e):
                eventExplain = eventNameE.get()
                if '百分比' in eventExplain:
                    value = 200
                elif '倍数' in eventExplain:
                    value = 2
                else:
                    value = 1
                eventArg1E.delete(0,tk.END)
                eventArg1E.insert(0,value)
            eventNameE = self.eventNameE
            eventNameE.bind('<<ComboboxSelected>>',select_new_event)
            CreateToolTip(eventNameE,textFunc=eventNameE.get)
            eventArg1E = self.eventArg1E

            refreshBtn = self.refreshEventBtn
            refreshBtn.config(command=lambda:print(f'活动已刷新({len(get_running_event())})'))

            deleteBtn = self.delEventBtn
            deleteBtn.config(command=del_event)
            
            addBtn = self.addEventBtn
            addBtn.config(command=set_event)
            CreateToolTip(addBtn,'添加删除后需重启服务器')
            
            return update_event_list_func
        
        buildTab_usual()
        build_Tab_Money()
        buildTab_mail()
        self.update_event_list_func = buildTab_event()

    def _buildTab_bubble(self):
        # 改同步：这是建泡点页签控件的函数，控件只能建在主线程；里面那条 get_online_uid() 只是查询
        bubbleUserTamplete = {
            'value':10,
            'interval':1,
            'timeStart':'00:00',
            'timeEnd':'23:59',
            'uids':[],
            'enable':0
        }
        def get_normal_bubble():
            bubbleDict = cacheM.config.get('BUBBLE',{})
            bubbleNormal = bubbleDict.get('normal',{
                    'value':10,
                    'interval':1,
                    'timeStart':'00:00',
                    'timeEnd':'23:59',
                    'enable':0
                    })
            
            
            self.bubbleIntervalE1.delete(0,tk.END)
            self.bubbleIntervalE1.insert(0,bubbleNormal['interval'])
            self.bubbleValueE1.delete(0,tk.END)
            self.bubbleValueE1.insert(0,bubbleNormal['value'])
            self.startHourE.delete(0,tk.END)
            self.startHourE.insert(0,bubbleNormal['timeStart'].split(':')[0])
            self.startMinE.delete(0,tk.END)
            self.startMinE.insert(0,bubbleNormal['timeStart'].split(':')[1])
            self.stopHourE.delete(0,tk.END)
            self.stopHourE.insert(0,bubbleNormal['timeEnd'].split(':')[0])
            self.stopMinE.delete(0,tk.END)
            self.stopMinE.insert(0,bubbleNormal['timeEnd'].split(':')[1])
            self.enableBubbleVar.set(bubbleNormal['enable'])
            bubbleDict['normal'] = bubbleNormal
            cacheM.config['BUBBLE'] = bubbleDict
            cacheM.save_config()

            
            return bubbleDict
        def enable_bubble():
            
            bubbleDict = cacheM.config.get('BUBBLE',{})
            

            enableStat = self.enableBubbleVar.get()
            bubbleNormal = bubbleDict.get('normal')
            bubbleNormal['enable'] = enableStat

            enableStat2 = self.enableBubbleVar2.get()
            bubbleID = self.bubbleIDE.get()
            bubbleDict[bubbleID]['enable'] = enableStat2
            cacheM.config['BUBBLE'] = bubbleDict
            cacheM.save_config()
            print(bubbleDict)

        def add_uid():
            aName = self.bubbleUIDE.get()
            try:
                uidINT = int(aName)
            except:
                uidINT = 0
            try:
                uNameINT = int(sqlM.getUID(aName))
            except:
                uNameINT = 0
            if uidINT==0 and uNameINT==0:
                messagebox.askokcancel('未查询到账号','请检查输入的账号是否正确')
                return False
            elif uidINT!=0 and uNameINT!=0:
                res = messagebox.askyesnocancel('查询到UID和用户名','选择是添加UID，选择否添加用户名')
                if res==True:
                    uid = uidINT
                elif res==False:
                    uid = uNameINT 
                else:
                    return False
            else:
                uid = max(uidINT,uNameINT)
            bubbleDict = cacheM.config.get('BUBBLE',{})
            bubbleID = self.bubbleIDE.get()
            bubbleDict[bubbleID]['uids'].append(uid)
            bubbleDict[bubbleID]['uids'] = list(set(bubbleDict[bubbleID]['uids']))
            cacheM.config['BUBBLE'] = bubbleDict
            cacheM.save_config()
            self.infoSvar.set(f'已添加账号[{uid}]')
            print(f'泡点[{bubbleID}]已添加账号[{uid}]')
            select_bubble(None)

        def rmUID():
            sels = self.bubbleAccountTree.selection()
            bubbleDict = cacheM.config.get('BUBBLE',{})
            for sel in sels:
                uid = self.bubbleAccountTree.item(sel)['values'][0]
                bubbleID = self.bubbleIDE.get()
                try:
                    bubbleDict[bubbleID]['uids'].remove(uid)
                except:
                    pass
            cacheM.config['BUBBLE'] = bubbleDict
            cacheM.save_config()
            select_bubble(None)

        
        def save_bubble_normal():
            bubbleDict = cacheM.config.get('BUBBLE',{})
            bubbleNormal = bubbleDict.get('normal')
            bubbleNormal['interval'] = int(self.bubbleIntervalE1.get())
            bubbleNormal['value'] = int(self.bubbleValueE1.get())
            bubbleNormal['timeStart'] = f'{self.startHourE.get()}:{self.startMinE.get()}'
            bubbleNormal['timeEnd'] = f'{self.stopHourE.get()}:{self.stopMinE.get()}'
            cacheM.save_config()
            messagebox.showinfo('提示','泡点配置已保存')

        def save_bubble_uid():
            bubbleID = self.bubbleIDE.get()
            bubbleDict = cacheM.config.get('BUBBLE',{})
            bubbleDict[bubbleID]['interval'] = int(self.bubbleIntervalE2.get())
            bubbleDict[bubbleID]['value'] = int(self.bubbleValueE2.get())
            bubbleDict[bubbleID]['timeStart'] = f'{self.startHourE2.get()}:{self.startMinE2.get()}'
            bubbleDict[bubbleID]['timeEnd'] = f'{self.stopHourE2.get()}:{self.stopMinE2.get()}'
            cacheM.save_config()
            messagebox.showinfo('提示',f'账号泡点[{bubbleID}]配置已保存')


        def select_bubble(e):
            bubbleID = self.bubbleIDE.get()
            bubbleIDDict = cacheM.config.get('BUBBLE').get(bubbleID,bubbleUserTamplete.copy())
            self.bubbleIntervalE2.delete(0,tk.END)
            self.bubbleIntervalE2.insert(0,bubbleIDDict['interval'])
            self.bubbleValueE2.delete(0,tk.END)
            self.bubbleValueE2.insert(0,bubbleIDDict['value'])
            self.startHourE2.delete(0,tk.END)
            self.startHourE2.insert(0,bubbleIDDict['timeStart'].split(':')[0])
            self.startMinE2.delete(0,tk.END)
            self.startMinE2.insert(0,bubbleIDDict['timeStart'].split(':')[1])
            self.stopHourE2.delete(0,tk.END)
            self.stopHourE2.insert(0,bubbleIDDict['timeEnd'].split(':')[0])
            self.stopMinE2.delete(0,tk.END)
            self.stopMinE2.insert(0,bubbleIDDict['timeEnd'].split(':')[1])
            self.enableBubbleVar2.set(bubbleIDDict['enable'])

            self.bubbleAccountTree.delete(*self.bubbleAccountTree.get_children())
            uids = bubbleIDDict['uids']
            onlineUIDs = sqlM.get_online_uid()
            
            for uid in uids:
                if uid in onlineUIDs.keys():
                    values = [uid,'在线']
                else:
                    values = [uid,'']
                self.bubbleAccountTree.insert('',tk.END,values=values)
            cacheM.config['BUBBLE'][bubbleID] = bubbleIDDict
            
        
        @inThread
        def bubble_RUN():
            # check bubble every 60s
            @inThread
            def sendBubble():
                timeNow = time.time()
                timeNow_=datetime.datetime.now()
                onlineUIDs = sqlM.get_online_uid()
                for uid in onlineUIDs.keys():
                    onlineStat = onlineDict.get(uid)
                    if onlineStat is None:
                        onlineDict[uid] = timeNow
                        continue
                for uid in list(onlineDict.keys()):
                    if uid not in onlineUIDs.keys():
                        onlineDict.pop(uid)
                uidBubbleValueDict = {uid:{'bubbles':[],'value':0} for uid in onlineUIDs.keys()}
                ignorePrivate = runOnUi(self.privateIPVar.get)==0   # IntVar 只能在主线程读
                for bubbleID,bubbleIDDict in cacheM.config.get('BUBBLE').items():
                    bubbleName = bubbleID #if not isinstance(bubbleID,int) else f'泡点{bubbleID}'
                    if bubbleIDDict['enable']==0:
                        continue
                    timeStart = bubbleIDDict['timeStart']
                    timeEnd = bubbleIDDict['timeEnd']
                    timeStart = datetime.datetime.fromtimestamp(timeNow).replace(hour=int(timeStart.split(':')[0]),minute=int(timeStart.split(':')[1]),second=0,microsecond=0)
                    timeEnd = datetime.datetime.fromtimestamp(timeNow).replace(hour=int(timeEnd.split(':')[0]),minute=int(timeEnd.split(':')[1]),second=0,microsecond=0)
                    if timeNow_>timeEnd or timeNow_<timeStart:
                        continue

                    for uid in onlineUIDs.keys():
                        if bubbleIDDict.get('uids') is not None:
                            if uid not in bubbleIDDict['uids']:
                                continue
                        if ignorePrivate and ipaddress.ip_address(onlineUIDs[uid]).is_private:
                            continue
                        if timeNow==onlineDict[uid]:
                            continue
                        if int((timeNow-onlineDict[uid])/60)%bubbleIDDict['interval']!=0:
                            continue
                        uidBubbleValueDict[uid]['bubbles'].append(bubbleName)
                        uidBubbleValueDict[uid]['value'] += bubbleIDDict['value']
                
                for uid,uBubbleDict in uidBubbleValueDict.items():
                    value = uBubbleDict['value']
                    if value==0:
                        continue
                    sqlM.charge_crea(uid,value,'cera_point')
                    timeString = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timeNow))
                    print(f'[{timeString}] 账号[{uid}] +[{value}]泡点,泡点列表{uBubbleDict["bubbles"]}')

            startTime = time.time()
            onlineDict = {}
            while True:
                try:
                    sendBubble()
                except Exception as e:
                    print(f'泡点发送错误{e}')
                time.sleep(61 - (time.time()-startTime)%60)

        get_normal_bubble()
        self.bubbleIDE.bind('<<ComboboxSelected>>',select_bubble)
        self.bubbleIDE.config(values=[f'泡点{i}' for i in range(1,6)])
        self.bubbleIDE.set('泡点1')
        select_bubble(None)

        self.saveBubbleBtn1.config(command=save_bubble_normal)
        self.saveBubbleBtn2.config(command=save_bubble_uid)

        self.enableBubbleBtn1.config(command=enable_bubble)
        self.enableBubbleBtn2.config(command=enable_bubble)

        self.addBubbleUIDBtn.config(command=add_uid)
        self.rmBubbleUIDBtn.config(command=rmUID)

        box = self.bubbleAccountTree
        bar = self.bubbleAccountBar
        bar.config(command=box.yview)
        box.config(yscrollcommand=bar.set)
        
        bubble_RUN()


        return True

