'''角色与物品页签（时装/宠物/邮件）（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppTabCharac:
    def _buildtab_itemTab_creature(self,creatureF:creatureFeame.CreatureframeWidget,tabName=' 宠物 '):
        def deleteItems():
            if not messagebox.askokcancel('删除确认',f'确定删除{tabName}所选物品？'):
                return False
            deleteIDs = []
            for sel in itemsTree_now.selection():
                delID = itemsTree_now.item(sel)['values'][0]
                deleteIDs.append(delID)
            
            print(f'删除{deleteIDs}')
            tableName = globalNonBlobs_map[tabName]
            for ui_id in deleteIDs:
                if sqlM.delNoneBlobItem(ui_id,tableName):
                    print('====删除成功====\n')
                else:
                    print('====删除失败，请检查数据库连接状况====\n')
            self.blobCommitExFunc(self.cNo)
            self.selectCharac()


        itemsTree_now = creatureF.itemsTreev_now
        self.currentTreeViews[tabName] = itemsTree_now
        self.itemsTreevs_now[tabName] = itemsTree_now
        delBtn = creatureF.deleteBtn
        delBtn.config(command=deleteItems)

    def _buildtab_itemTab_avatar(self,avatarF:avatarFrame.AvatarframeWidget,tabName=' 时装 '):
        def deleteItems():
            if not messagebox.askokcancel('删除确认',f'确定删除{tabName}所选物品？'):
                return False
            deleteIDs = []
            for sel in itemsTree_now.selection():
                delID = itemsTree_now.item(sel)['values'][0]
                deleteIDs.append(delID)
            
            print(f'删除{deleteIDs}')

            tableName = globalNonBlobs_map[tabName]
            for ui_id in deleteIDs:
                if sqlM.delNoneBlobItem(ui_id,tableName):
                    print('====删除成功====\n')
                else:
                    print('====删除失败，请检查数据库连接状况====\n')
            self.blobCommitExFunc(self.cNo)
            self.selectCharac()

        def enableHidden():
            value =int(hiddenCom.get().split('-')[0])
            if not messagebox.askokcancel('提交确认',f'确定修改{tabName}所选物品？'):
                return False
            editIDS = []
            for sel in itemsTree_now.selection():
                delID = itemsTree_now.item(sel)['values'][0]
                editIDS.append(delID)
            log('编辑非BLOB')
            tableName = globalNonBlobs_map[tabName]
            for ui_id in editIDS:
                if sqlM.enable_Hidden_Item(ui_id,tableName,value):
                    print('====修改成功====\n')
                else:
                    print('====修改失败，请检查数据库连接状况====\n')
            self.selectCharac()


        itemsTree_now = avatarF.itemsTreev_now
        self.currentTreeViews[tabName] = itemsTree_now
        itemsTreev_now = itemsTree_now
        self.itemsTreevs_now[tabName] = itemsTreev_now

        hiddenCom = avatarF.avatarHiddenE
        hiddenCom.config(values=['0-None']+[f'{i+1}-{value}' for i,value in enumerate(cacheM.avatarHiddenList[0])],width=int(WIDTH*10))

        hiddenCom.set('0-None')
        self.hiddenCom = hiddenCom
        addHiddenBtn = avatarF.addHiddenBtn
        addHiddenBtn.config(command=enableHidden)
        delBtn = avatarF.deleteBtn
        delBtn.config(command=deleteItems)

    def _buildtab_itemTab_mail(self,mailF:mailFrame.MailframeWidget,tabName=' 邮件 '):
        def deleteItems():
            if not messagebox.askokcancel('删除确认',f'确定删除{tabName}所选物品？'):
                return False
            deleteIDs = []
            for sel in itemsTree_now.selection():
                delID = itemsTree_now.item(sel)['values'][0]
                deleteIDs.append(delID)
            print(f'删除{deleteIDs}')
            tableName = globalNonBlobs_map[tabName]
            for ui_id in deleteIDs:
                if sqlM.delNoneBlobItem(ui_id,tableName):
                    print('====删除成功====\n')
                else:
                    print('====删除失败，请检查数据库连接状况====\n')
            self.blobCommitExFunc(self.cNo)
            self.selectCharac()
    
        itemsTree_now = mailF.itemsTreev_now
        self.currentTreeViews[tabName] = itemsTree_now
        itemsTreev_now = mailF.itemsTreev_now
        self.itemsTreevs_now[tabName] = itemsTreev_now
        delBtn = mailF.deleteBtn
        delBtn.config(command=deleteItems)

    def _buildtab_charac(self,characF:characFrame.CharacframeWidget,tabName):
        def clear_tab():
            '''清空角色信息页'''
            nameE.config(state='normal')
            nameE.delete(0,tk.END)
            levE.delete(0,tk.END)
            growTypeE.set('')
            jobE.set('')
            wakeFlgE.set(0)
        def commit():
            if not messagebox.askokcancel('修改确认',f'确定修改角色数据信息？\n请保证账号不在线或正在登陆其他角色'):
                return False
            cName = nameE.get()
            nameLen = len(cName.encode())
            if nameLen>20:
                cName = cName.encode()[:20].decode(errors='ignore')
                CreateOnceToolTip(nameE,'名字超长，自动裁切')
                nameE.delete(0,tk.END)
                nameE.insert(0,cName)
            lev = int(levE.get())
            job = int(jobE.get().split('-')[0])
            growType = int(growTypeE.get().split('-')[0])
            growType += int(wakeFlgE.get()) * 0x10
            expert_job = int(jobE2.get().split('-')[0])
            kwDict = {
                'charac_name':cName,
                'job':job,
                'lev':lev,
                'grow_type':growType,
                'VIP':isVIP.get(),
                'expert_job':expert_job
            }
            print(kwDict)
            if cName==self.cName:
                kwDict.pop('charac_name')

            sqlM.set_charac_info(self.cNo,**kwDict)
            if isReturnUser.get()==1:
                sqlM.set_return_user(self.cNo)
            else:
                sqlM.clear_return_user(self.cNo)
            return True
      
        def fill_charac_Info_tab():
            '''根据当前选中的cNo填充角色数据'''
            cInfos = sqlM.getCharacterInfo(cNo=self.cNo)
            #print(cInfos)
            if len(cInfos)==0:
                cName = self.characInfos[self.cNo].get('name')
                lev = self.characInfos[self.cNo].get('lev')
                job = self.characInfos[self.cNo].get('job')
                growType = self.characInfos[self.cNo].get('growType') % 16
                wakeFlg = self.characInfos[self.cNo].get('growType') // 16
                expert_job = self.characInfos[self.cNo].get('expert_job')
            else:
                uid,cNo,cName,lev,job,growType,deleteFlag,expert_job = cInfos[0]
                wakeFlg = int(growType)//16
                growType = int(growType)%16
                
            #VIP = 
            isVIP.set(sqlM.read_VIP(self.cNo))
            isReturnUser.set(sqlM.read_return_user(self.cNo))
            if self.cNo in self.banedDictCno.keys():
                self.isBanedUser.set(1)
            else:
                self.isBanedUser.set(0)

            clear_tab()
            
            nameE.insert(0,cName)
            levE.insert(0,lev)
            jobE.set(f'{job}-{cacheM.jobDict.get(job).get(0)}')
            jobE2.set(f'{expert_job}-{expert_jobMap.get(expert_job)}')
            set_grow_type()
            growTypeE.set(f'{growType}-{cacheM.jobDict.get(job).get(growType)}')
            wakeFlgE.set(wakeFlg)
        
        @inThread
        def set_ban_var(e:tk.Event=None):
            time.sleep(0.3)
            if self.isBanedUser.get()==1:
                sqlM.set_baned(self.uid)
                messagebox.showinfo('提示','已封禁该账号')
            else:
                sqlM.resume_baned(self.uid)
                messagebox.showinfo('提示','已解封该账号')
            self.refill_baned_tree()
        
        def enable_auction(y=None,m=None):
            if y==None:
                y = time.strftime("%Y", time.localtime())
            if m==None:
                m = time.strftime("%m", time.localtime())
            sql = f'''CREATE TABLE IF NOT EXISTS `auction_history_{y}{m}`(
                    `auction_id` bigint(20) unsigned NOT NULL DEFAULT '0',
                    `start_time` datetime DEFAULT NULL,
                    `occ_time` datetime DEFAULT NULL,
                    `event_type` tinyint(4) DEFAULT NULL,
                    `owner_id` int(11) DEFAULT NULL,
                    `buyer_id` int(11) DEFAULT NULL,
                    `price` int(11) DEFAULT NULL,
                    `seal_flag` tinyint(4) DEFAULT NULL,
                    `item_id` int(10) unsigned DEFAULT NULL,
                    `add_info` int(11) DEFAULT NULL,
                    `upgrade` tinyint(3) unsigned DEFAULT NULL,
                    `amplify_option` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `amplify_value` mediumint(8) unsigned NOT NULL DEFAULT '0',
                    `seal_cnt` tinyint(3) unsigned DEFAULT NULL,
                    `endurance` smallint(5) unsigned DEFAULT NULL,
                    `extend_info` int(10) unsigned DEFAULT NULL,
                    `owner_postal_id` int(10) unsigned DEFAULT NULL,
                    `buyer_postal_id` int(10) unsigned DEFAULT NULL,
                    `expire_time` int(10) unsigned NOT NULL DEFAULT '0',
                    `unit_price` int(10) unsigned NOT NULL DEFAULT '0',
                    `random_option` varchar(14) NOT NULL DEFAULT '',
                    `roi_high_key` bigint(20) NOT NULL DEFAULT '0',
                    `roi_low_key` int(11) NOT NULL DEFAULT '0',
                    `seperate_upgrade` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `commission` int(11) unsigned NOT NULL DEFAULT '0',
                    `owner_type` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `item_guid` varbinary(10) NOT NULL DEFAULT '',
                    PRIMARY KEY (`auction_id`),
                    KEY `idx_buyer_id` (`buyer_id`) USING BTREE,
                    KEY `idx_occ_time` (`occ_time`) USING BTREE,
                    KEY `idx_owner_id` (`owner_id`) USING BTREE
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;'''
            sqlM.execute_and_commit('taiwan_cain_auction_gold',sql)

            sql = f'''CREATE TABLE IF NOT EXISTS `auction_history_buyer_{y}{m}` (
                    `auction_id` bigint(20) unsigned DEFAULT NULL,
                    `occ_time` datetime DEFAULT NULL,
                    `pre_buyer_id` int(11) DEFAULT NULL,
                    `buyer_id` int(11) DEFAULT NULL,
                    `pre_price` int(11) DEFAULT NULL,
                    `price` int(11) DEFAULT NULL,
                    `pre_buyer_postal_id` int(10) unsigned DEFAULT NULL,
                    KEY `idx_auction_id` (`auction_id`) USING BTREE,
                    KEY `idx_buyer_id` (`buyer_id`) USING BTREE
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8 ROW_FORMAT=COMPACT;'''
            sqlM.execute_and_commit('taiwan_cain_auction_gold',sql)


            sql = f'''CREATE TABLE `auction_history_{y}{m}` (
                    `auction_id` bigint(20) unsigned NOT NULL DEFAULT '0',
                    `start_time` datetime DEFAULT NULL,
                    `occ_time` datetime DEFAULT NULL,
                    `event_type` tinyint(4) DEFAULT NULL,
                    `owner_id` int(11) DEFAULT NULL,
                    `buyer_id` int(11) DEFAULT NULL,
                    `price` int(11) DEFAULT NULL,
                    `seal_flag` tinyint(4) DEFAULT NULL,
                    `item_id` int(10) unsigned DEFAULT NULL,
                    `add_info` int(11) DEFAULT NULL,
                    `upgrade` tinyint(3) unsigned DEFAULT NULL,
                    `amplify_option` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `amplify_value` mediumint(8) unsigned NOT NULL DEFAULT '0',
                    `seal_cnt` tinyint(3) unsigned DEFAULT NULL,
                    `endurance` smallint(5) unsigned DEFAULT NULL,
                    `extend_info` int(10) unsigned DEFAULT NULL,
                    `owner_postal_id` int(10) unsigned DEFAULT NULL,
                    `buyer_postal_id` int(10) unsigned DEFAULT NULL,
                    `expire_time` int(10) unsigned NOT NULL DEFAULT '0',
                    `unit_price` int(10) unsigned NOT NULL DEFAULT '0',
                    `random_option` varchar(14) NOT NULL DEFAULT '',
                    `roi_high_key` bigint(20) NOT NULL DEFAULT '0',
                    `roi_low_key` int(11) NOT NULL DEFAULT '0',
                    `seperate_upgrade` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `commission` int(11) unsigned NOT NULL DEFAULT '0',
                    `owner_type` tinyint(3) unsigned NOT NULL DEFAULT '0',
                    `item_guid` varbinary(10) NOT NULL DEFAULT '',
                    PRIMARY KEY (`auction_id`),
                    KEY `idx_owner_id` (`owner_id`) USING BTREE,
                    KEY `idx_buyer_id` (`buyer_id`) USING BTREE,
                    KEY `idx_occ_time` (`occ_time`) USING BTREE
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
                '''
            sqlM.execute_and_commit('taiwan_cain_auction_cera',sql)

            sql = f'''CREATE TABLE `auction_history_buyer_{y}{m}` (
                    `auction_id` bigint(20) unsigned DEFAULT NULL,
                    `occ_time` datetime DEFAULT NULL,
                    `pre_buyer_id` int(11) DEFAULT NULL,
                    `buyer_id` int(11) DEFAULT NULL,
                    `pre_price` int(11) DEFAULT NULL,
                    `price` int(11) DEFAULT NULL,
                    `pre_buyer_postal_id` int(10) unsigned DEFAULT NULL,
                    KEY `idx_auction_id` (`auction_id`) USING BTREE,
                    KEY `idx_buyer_id` (`buyer_id`) USING BTREE
                    ) ENGINE=MyISAM DEFAULT CHARSET=utf8;
                '''
            sqlM.execute_and_commit('taiwan_cain_auction_cera',sql)
            messagebox.showinfo('提示','已在数据库中添加拍卖行与金币寄售表格，请重启服务端程序。\n如拍卖行无法启动请尝试清空taiwan_cain_auction_gold数据库中的auction_main数据表')
            return True
        self.clear_charac_tab_func = clear_tab
        self.fill_charac_tab_fun = fill_charac_Info_tab
        self.cNo
        
        characMainFrame = characF
        


        characF.saveStartBtn.config(command=ps.saveStart)
        CreateToolTip(characF.saveStartBtn,'读取正在运行的DNF进程\n生成一键登录exe')
        self.PVF_CACHE_EDIT_OPEN_FLG = False

        btn = characF.pvfCacheMBtn
        btn.config(command=self.open_PVF_Cache_Edit)
        CreateToolTip(btn,'修改缓存数据\n导出装备道具列表为CSV')

        #btn = characF.pvfToolBtn
        #btn.config(command=self._open_PVF_Editor)
        #CreateToolTip(btn,'开启PVF编辑工具（测试）')

        auctionBtn = characF.enableAuctionBtn
        auctionBtn.config(command=enable_auction)
        CreateToolTip(auctionBtn,'开启拍卖行与金币寄售，需要手动重启服务端\n当PVF装备锻造可以超过7时，拍卖行无法搜索物品')


        updateCheckVar = characF.updateCheckVar
        updateCheckVar.set(1 if cacheM.config.get('UPDATE_CHECK') is None or cacheM.config.get('UPDATE_CHECK')==1 else 0)
        def setUpdate():
            cacheM.config['UPDATE_CHECK'] = updateCheckVar.get()
            cacheM.save_config()
            if updateCheckVar.get()==1:
                self.check_Update()
        if self.check_update_flg:
            checkUpdateBtn = characF.checkUpdateBtn
            checkUpdateBtn.config(command=setUpdate)
            if updateCheckVar.get()==1:
                
                self.mainwindow.after(2000,self.check_Update)
        HDVar = characF.HDResolutionVar
        HDVar.set(cacheM.config.get('HD_RESOLUTION',0))
        
        def setHD():
            cacheM.config['HD_RESOLUTION'] = HDVar.get()
            cacheM.save_config()
        HDBtn = characF.HDresolutionBtn#HDResolutionBtn
        
        #HDBtn.config(command=setHD)
        #CreateToolTip(HDBtn,'开启高清分辨率，重启程序后生效')


        nameE = characF.nameE
        self.nameEditE = nameE
        levE = characF.levE
        levE.config(to=999,from_=1)
        isVIP = characF.isVIP
        def set_grow_type(e=None):
            growTypeE.config(values=[f'{item[0]}-{item[1]}' for item in cacheM.jobDict.get(int(jobE.get().split('-')[0])).items()])

        jobE2 = characF.jobE2
        jobE2.config(values=[f'{key}-{value}' for key,value in expert_jobMap.items()])
        jobE = characF.jobE
        jobE.config(values=[f'{item[0]}-{item[1][0]}'  for item in cacheM.jobDict.items()])
        jobE.bind('<<ComboboxSelected>>',set_grow_type)
        self.jobE = jobE

        growTypeE = characF.growTypeE
        wakeFlgE = characF.wakeFlgE
        wakeFlgE.config(state='readonly',values=[0,1,2])

        isReturnUser = characF.isReturnUser
        commitBtn = characF.commitBtn
        commitBtn.config(command=commit)
        GitHubFrame(characF.gitHubFrame).pack()

        self.cInfoSetBanedBtn.bind('<Button-1>',set_ban_var)

    
