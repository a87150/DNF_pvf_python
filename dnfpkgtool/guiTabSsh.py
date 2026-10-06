'''SSH/封禁/数据库连接页签（GuiApp 的方法体，组合见 dnfpkgtool/__main__.py）'''
from dnfpkgtool.appCommon import *


class GuiAppTabSsh:
    def _buildFrame_SSH(self):
        def connect(show=True,key=False):
            def inner():
                if self.connectedFlg:
                    try:
                        ssh.close()
                        self.transPort.close()
                    except:
                        pass
                ip = runOnUi(ipE.get)
                port = int(runOnUi(portE.get))
                user = runOnUi(userE.get)
                self.connectingFlg = True
                if key:
                    keyPath = runOnUi(askopenfilename,filetypes=[('密钥文件','*.pub'),('所有文件','*.*')])
                    if not keyPath:
                        return False
                    
                    try:
                        private_key  = paramiko.RSAKey.from_private_key_file(keyPath)
                    except Exception as e:
                        runOnUi(messagebox.showerror,'错误',f'密钥文件错误{e}')
                        return False
                    try:
                        ssh.connect(ip, username=user, port=port, pkey=private_key,timeout=3)
                        self.transPort = paramiko.Transport((ip,port))
                        self.transPort.connect(username=user, pkey=private_key)
                    except Exception as e:
                        if show:
                            print(f'连接失败 {e}')
                            runOnUi(self.title,f'连接失败 {e}')
                        self.connectedFlg = False
                        self.connectingFlg = False
                        return False
                    cacheM.config['SERVER_PWD'] = ''
                else:
                    pwd = runOnUi(pwdE.get)
                    try:
                        ssh.connect(ip, username=user, port=port, password=pwd,timeout=3)
                        self.transPort = paramiko.Transport((ip,port))
                        self.transPort.connect(username=user, password=pwd)
                        
                    except Exception as e:
                        if show:
                            print(f'连接失败 {e}')
                            runOnUi(self.title,f'连接失败 {e}')
                        self.connectedFlg = False
                        self.connectingFlg = False
                        return False
                    cacheM.config['SERVER_PWD'] = pwd
                cacheM.config['SERVER_IP'] = ip
                cacheM.config['SERVER_PORT'] = port
                cacheM.config['SERVER_USER'] = user
                cacheM.config['SERVER_CONFIGS'][ip] = {'port':port,'pwd':pwd,'user':user}
                cacheM.save_config()
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("ls /root")
                files = ['sh '+item.strip() for item in ssh_stdout.readlines()]
                for fileSelE in fileSelEList:
                    runOnUi(fileSelE.config,values=files)
                self.connectedFlg = True
                #self.ip = ip
                runOnUi(self.title,'服务器已连接！')
                self.connectingFlg = False
                runOnUi(configFrame,self.SSHDIYFrame,'normal')
            t = threading.Thread(target = inner)
            t.daemon = True
            t.start()        
        def run_server():
            def inner():
                nonlocal startingFlg
                if startingFlg:
                    print('服务器正在启动中！请点击停止服务器')
                    return False
                startingFlg = True
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sh /root/run")
                print('DNF服务器启动中...')
                while True:
                    res = ssh_stdout.readline()
                    print(res)
                    if res == '':
                        break
                    if 'Connect To Guild Server' in str(res):
                        print('服务器启动完成')
                        break
                    if 'success' in str(res).lower() or 'error' in str(res).lower():
                        print(str(res).strip())
                        insert2cmdLog(res)
                startingFlg = False
                
            t = threading.Thread(target=inner)
            t.daemon = True
            t.start()
        def stop_server():
            def inner():
                nonlocal startingFlg
                startingFlg = False
                runOnUi(self.title,'指令执行中...')
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sh /root/stop")
                ssh_stdout.readlines()
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sh /root/stop")
                ssh_stdout.readlines()
                print('服务器已停止')
                runOnUi(self.title,'服务器已停止')
            t = threading.Thread(target=inner)
            t.daemon = True
            t.start()

        def restart_channel():
            run_cmd('sh /root/run1')

        def insert2cmdLog(s:str):
            #self.shellLogE.config(state='normal')
            s = s+ '\n' if s[-1]!='\n' else s
            # 由 run_server / run_cmd 的后台线程调用，控件写入回主线程
            runOnUi(self.shellLogE.insert,tk.END,s)
            #self.shellLogE.config(state='disable')
            runOnUi(self.shellLogE.see,tk.END)

        def run_file(fileName):
            def inner():
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(f'sh "/root/{fileName}"')
                while True:
                    res = ssh_stdout.readline()
                    if res == '':
                        break
                    time.sleep(0.05)
                    runOnUi(self.title,res)
                runOnUi(self.title,f'{fileName}执行完毕')

            t = threading.Thread(target=inner)
            t.daemon = True
            t.start()

        def run_cmd(cmd='ls',endStr=None):
            def inner():
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                runOnUi(save_diy)
                t = 0
                while True:
                    try:
                        res = ssh_stdout.readline()
                        if res.replace('\n','') == '':
                            t += 1
                            if t==10: break
                        else:
                            t = 0
                            if endStr is not None and endStr in res:
                                break
                            insert2cmdLog(res)
                            print(res.replace('\n',''))
                        time.sleep(0.02)
                    except:
                        break
                #self.title(f'指令执行完毕')
                print(f'指令执行完毕')
                #time.sleep(60)

            t = threading.Thread(target=inner)
            t.daemon = True
            t.start()
            return t

        def load_diy():
            '''diyList = cacheM.config['DIY']
            for i,diy in enumerate(diyList):
                try:
                    fileSelEList[i].set(diy)
                except:
                    pass'''
            diyList = cacheM.config['DIY_2']
            for i,diy in enumerate(diyList):
                try:
                    cmdEList[i].insert(0,diy)
                except:
                    pass
        def save_diy():
            '''diyList = []
            for selE in fileSelEList:
                diyList.append(selE.get())
            cacheM.config['DIY'] = diyList'''
            diyList = []
            for selE in cmdEList:
                diyList.append(selE.get())
            cacheM.config['DIY_2'] = diyList
            cacheM.save_config()
        
        def uploadFile():
            def inner():
                def printTotals(transferred, toBeTransferred):
                    nonlocal time_now
                    if time.time() - time_now>1:
                        print("Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred))
                        runOnUi(self.title,"%.3fM/%.3fM" % (transferred/1e6, toBeTransferred/1e6))
                        time_now += 1

                pvfPath = runOnUi(askopenfilename,filetypes=[('DNF Script.pvf file','*.pvf')])                
                if pvfPath=='' or not Path(pvfPath).exists():
                    runOnUi(self.title,'文件错误')
                    return False
                print(pvfPath)
                sftp = paramiko.SFTPClient.from_transport(self.transPort)
                remote_path = r'/home/neople/game/Script.pvf'
                cmd = r'ls /home/neople/game/'
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
                res = ssh_stdout.readlines()
                #print(res)
                if len(res)<5:
                    runOnUi(self.title,'目标文件夹异常')
                    return False
                time_now = time.time()
                sftp.put(pvfPath,remote_path,callback=printTotals)
                runOnUi(self.title,'上传完成！')
                upPatch = runOnUi(messagebox.askokcancel,'上传完成，是否上传等级补丁？')
                if upPatch:
                    remote_path = r'/home/neople/game/df_game_r'
                    patchPath = runOnUi(askopenfilename)    
                    if patchPath=='':
                        runOnUi(self.title,'补丁文件错误')
                        return False
                    sftp.put(patchPath,remote_path,callback=printTotals)
            t = threading.Thread(target=inner)
            t.start()
    
        def lsDir(dirPath='/'):
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(f"ls {dirPath}")
            files = [item.strip() for item in ssh_stdout.readlines()]
            return files

        def downloadFile(filePath='',targetPath='',progressBarPos=[200,200],progressBarMaster=None):
            def showProgress(transferred, toBeTransferred):
                #print(transferred,toBeTransferred)
                nonlocal time_now
                if time.time() - time_now>1:
                    progressBar['maximum'] = toBeTransferred
                    # 进度值初始值
                    progressBar['value'] = transferred
                    progressBar.update()
                    time_now += 0.1

            # 使用paramiko下载文件到本机
            if progressBarMaster is None:
                progressBarMaster = self.master
            progressWin = tk.Toplevel(progressBarMaster)
            progressWin.geometry(f"+{progressBarPos[0]}+{progressBarPos[1]}")
            progressWin.overrideredirect(True)
            progressWin.focus_force()
            progressBar = ttk.Progressbar(progressWin)
            progressBar.pack()
            time_now = time.time()
            try:
                sftp = paramiko.SFTPClient.from_transport(self.transPort)
                sftp.get(filePath, targetPath,callback=showProgress)
            except:
                progressWin.destroy()
                return False
            progressWin.destroy()
            return True
            
        self.run_cmd = run_cmd
        self.lsDir = lsDir
        self.downloadFile = downloadFile
        self.connectingFlg = False
        self.connectedFlg = False
        import paramiko
        ssh = paramiko.SSHClient()
        self.ssh = ssh
        self.transPort:paramiko.Transport = None
        # 允许连接不在know_hosts文件中的主机
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        startingFlg = False
        config = cacheM.config
        if True:
            ipE = self.ipE2
            ipE.insert(0,config['SERVER_IP'])
            portE = self.portE2
            portE.insert(0,config['SERVER_PORT'])
            userE = self.userE2
            userE.insert(0,config['SERVER_USER'])
            pwdE = self.pwdE2
            pwdE.insert(0,config['SERVER_PWD'])
            SSHconBtn = self.sshConBtn
            SSHconBtn.config(command=connect)

            SSHKeyConBtn = self.SSHKeyConBtn
            SSHKeyConBtn.config(command=lambda:connect(key=True))

        #ttk.Separator(serverFrame, orient='horizontal').pack(fill='x')

        runBtn = self.runServerBtn
        runBtn.config(command=run_server)
        CreateToolTip(runBtn,'执行/root/run文件')
        stopBtn = self.stopServerBtn
        stopBtn.config(command=stop_server)
        CreateToolTip(stopBtn,'执行/root/stop文件')
        run1Btn = self.restartChBtn
        run1Btn.config(command=restart_channel)

        CreateToolTip(run1Btn,'执行/root/run1文件')
        uploadBtn = self.uploadPVFBtn
        uploadBtn.config(command=uploadFile)
        CreateToolTip(uploadBtn,'上传到/home/neople/game/Script.pvf并将原文件覆盖')

        cmdEList = [self.cmdE1,self.cmdE2,self.cmdE3,self.cmdE4]
        fileSelEList = cmdEList
        cmdRunBtnList = [self.runBtn1,self.runBtn2,self.runBtn3,self.runBtn4]
        for cmdRunBtn in cmdRunBtnList:
            cmdRunBtn.config(command=lambda:run_cmd(cmdEList[cmdRunBtnList.index(cmdRunBtn)].get()))
        
        configFrame(self.SSHDIYFrame,'disabled')

        load_diy()

    def _buildTab_Baned(self):
        punish_type_map = {
            1:'禁止登陆',
            4:'限制交易',
            11:'限制交易',
        }
        @inThread
        def refill_baned_tree():
            banedDict = sqlM.get_baned_Dict_detail()
            banedDictCno = {}
            rows = []
            for uid,BanInfo in banedDict.items():
                characs = sqlM.getCharacterInfo(uid=uid)
                for uid_,cNo,name,lev,job,growType,deleteFlag,expert_job in characs:
                    if deleteFlag==1:continue
                    jobDict = cacheM.jobDict.get(job)
                    if isinstance(jobDict,dict):
                        jobNew = jobDict.get(growType % 16)
                    else:
                        jobNew = growType % 16
                    punishTypeZh = punish_type_map.get(BanInfo['punish_type'],BanInfo['punish_type'])
                    values = [BanInfo['accountName'],uid,cNo,lev,name,jobNew,BanInfo['ip'],punishTypeZh]
                    banedDictCno[cNo] = {
                        'uid':uid,'name':name,'job':jobNew,'lev':lev,'ip':BanInfo['ip']
                    }
                    rows.append(values)
            self.banedDictCno = banedDictCno
            # 行组好后一次性交回主线程刷控件（原来在后台线程直接 delete/insert）
            def fill_baned_tree(rows):
                self.banedTreeV.delete(*self.banedTreeV.get_children())
                for values in rows:
                    self.banedTreeV.insert('',tk.END,values=values)
            runOnUi(fill_baned_tree,rows)
        
        def set_baned_a():
            aName = self.banAnameE.get()
            punishType = self.punishTypeE.get()
            if punishType=='禁止登陆':
                punishTypeValue = 1
            elif punishType=='限制交易':
                punishTypeValue = 4
            try:
                uidINT = int(aName)
            except:
                uidINT = 0
            try:
                uidSTR = int(sqlM.getUID(aName))
            except:
                uidSTR = 0
            if uidINT==0 and uidSTR==0:
                messagebox.askokcancel('未查询到账号','请检查输入的账号是否正确')
                return False
            elif uidINT!=0 and uidSTR!=0:
                res = messagebox.askyesnocancel('查询到UID和用户名','选择是封禁UID，选择否封禁用户名')
                if res==True:
                    uid = uidINT
                elif res==False:
                    uid = uidSTR
                else:
                    return False
            else:
                uid = max(uidINT,uidSTR)
            if not messagebox.askokcancel('封禁确认',f'确定封禁账号[{uid}]？'):
                return False
            sqlM.resume_baned(uid)
            sqlM.set_baned(uid,punish_type=punishTypeValue)
            print(f'封禁完成-{uid}')
            self.refill_baned_tree()

        
        def set_baned_c():
            cName = self.banCnameE.get()
            characs = sqlM.getCharacterInfo(cName=cName)
            punishType = self.punishTypeE.get()
            if punishType=='禁止登陆':
                punishTypeValue = 1
            elif punishType=='限制交易':
                punishTypeValue = 4
            if len(characs)>1:
                messagebox.askokcancel('查询到多个角色','请在首页进行查询后，在GM页面设置封禁')
                return False
            elif len(characs)==1:
                if not messagebox.askokcancel('封禁确认',f'确定封禁角色{characs[0]}？'):
                    return False
                uid = characs[0][0]
                sqlM.resume_baned(uid)
                sqlM.set_baned(uid,punish_type=punishTypeValue)
                print(f'封禁完成-{uid}')
                self.refill_baned_tree()
            else:
                messagebox.askokcancel('未查询到角色','请检查输入的角色名是否正确')
                return False

        def set_resume():
            if not messagebox.askokcancel('解封确认','确定解封当前选中的角色？'):
                return False
            sels = self.banedTreeV.selection()
            for sel in sels:
                uid = self.banedTreeV.item(sel)['values'][1]
                sqlM.resume_baned(uid)
                print(f'解封账号-{uid}')
            self.refill_baned_tree()

        self.setBanedABtn.config(command=set_baned_a)
        self.setBanedCBtn.config(command=set_baned_c)
        self.resumeBanedBtn.config(command=set_resume)
        self.punishTypeE.set('禁止登陆')
        self.punishTypeE.config(state='readonly')
        
        self.refill_baned_tree = refill_baned_tree
        self.banedDictCno = {}

    def save_resolution(self):
        width = self.mainwindow.winfo_width()
        height = self.mainwindow.winfo_height()
        cacheM.config['RESOLUTION'] = f'{width}x{height}'
        cacheM.save_config()
        print('分辨率已保存')
        #self.infoLabel.config(text=f'分辨率已保存 {width}x{height}')
        self.infoSvar.set(f'分辨率已保存 {width}x{height}')


    def fill_tab_treeviews(self,taskID=0):
        '''根据当前本地的blob和非blob字段填充数据（不包括角色信息）'''
        self.selectedCharacItemsDict = {}
        for key in self.editedItemsDict.keys():
            self.editedItemsDict[key] = {}    #清空编辑的对象
        
        # 填充blob字段
        #print(self.globalCharacBlobs.keys())
        #print(len(self.globalCharacBlobs.keys()))
        for tabName,currentTabBlob in self.globalCharacBlobs.items():#替换填充TreeView
            #print(tabName)
            CharacItemsList = []
            itemsTreev_now = self.itemsTreevs_now[tabName]
            itemsTreev_now.delete(*itemsTreev_now.get_children())
            
            CharacItemsList = sqlM.unpackBLOB_Item(currentTabBlob)
            #print(len(CharacItemsList))
            if len(CharacItemsList)==0:
                print(f'{tabName}字段解压错误或不存在')
            CharacItemsDict = {}
            self.currentItemDict = {}
            for values in CharacItemsList:
                index, dnfItemSlot = values
                name = str(cacheM.ITEMS_dict.get(dnfItemSlot.id))
                CharacItemsDict[index] = dnfItemSlot
            self.selectedCharacItemsDict[tabName] = CharacItemsDict
            #print('字段处理完成')
            if len(self.loadPkgTaskList)>taskID+1: return
            self.itemInfoClrFuncs[tabName]()    #清除物品信息显示
            self.fillTreeFunctions[tabName]()   #填充treeview
            #print(tabName,'填充完毕')
        #print('blob字段填充完毕')
        self.hiddenCom.set('0-None')
        self.checkBloblegal()   #检查物品合法

        tabName = ' 宠物 '
        currentTabItems = self.globalCharacNonBlobs.get(tabName)
        try:
            itemsTreev_now = self.itemsTreevs_now[tabName]
            itemsTreev_now.delete(*itemsTreev_now.get_children())
            CharacNoneBlobItemsDict = {}
            for values in currentTabItems:
                if len(self.loadPkgTaskList)>taskID+1: return
                itemsTreev_now.insert('',tk.END,values=values)
                CharacNoneBlobItemsDict[values[0]] = values
            self.selectedCharacItemsDict[tabName] = CharacNoneBlobItemsDict
        except:
            print(f'{tabName}加载失败')
        
        tabName = ' 时装 '
        currentTabItems = self.globalCharacNonBlobs.get(tabName)
        try:
            itemsTreev_now = self.itemsTreevs_now[tabName]
            itemsTreev_now.delete(*itemsTreev_now.get_children())
            CharacNoneBlobItemsDict = {}
            for values in currentTabItems:
                if len(self.loadPkgTaskList)>taskID+1: return
                try:
                    values[3] = cacheM.avatarHiddenList[0][values[3]-1] if values[3]>0 else '---'
                except:
                    pass
                itemsTreev_now.insert('',tk.END,values=values)
                CharacNoneBlobItemsDict[values[0]] = values
            self.selectedCharacItemsDict[tabName] = CharacNoneBlobItemsDict
        except:
            print(f'{tabName}加载失败')
        
        tabName = ' 邮件 '
        currentTabItems = self.globalCharacNonBlobs.get(tabName)
        try:
            itemsTreev_now = self.itemsTreevs_now[tabName]
            itemsTreev_now.delete(*itemsTreev_now.get_children())
            CharacNoneBlobItemsDict = {}
            for values in currentTabItems:
                if len(self.loadPkgTaskList)>taskID+1: return
                #print(values)
                try:
                    itemID = values[2]
                    values[1] = cacheM.ITEMS_dict.get(itemID)
                    if cacheM.equipmentDict.get(itemID) is not None:
                        values[4] = 1 
                except:
                    pass
                itemsTreev_now.insert('',tk.END,values=values)
                CharacNoneBlobItemsDict[values[0]] = values
            self.selectedCharacItemsDict[tabName] = CharacNoneBlobItemsDict
        except:
            print(f'{tabName}加载失败')
        if len(self.loadPkgTaskList)>taskID+1: return
        self.questFrame.load_quest()
        self.infoSvar.set(f' 加载角色：{self.cName}({self.cNo})')
        self.fillingFlg = False

    def run(self):
        self.mainwindow.mainloop()



    def connectSQL(self,dbConn=None):
        def inner():
            config = cacheM.config
            config['DB_IP'] = runOnUi(self.db_ipE.get)
            config['DB_PORT'] = int(runOnUi(self.db_portE.get))
            config['DB_USER'] = runOnUi(self.db_userE.get)
            config['PVF_PATH'] = cacheM.config.get('PVF_PATH')
            runOnUi(self.mainwindow.update)
            pwd = runOnUi(self.db_pwdE.get)
            if pwd!='******':
                config['DB_PWD'] = pwd
            else:
                pwd = config['DB_PWD']
            #log(str(config))
            cacheM.config = config
            runOnUi(self.db_conBTN.config,text='连接数据库',state='normal')
            sqlresult = sqlM.connect(print,conn=dbConn)
            if '失败' not in sqlresult:  
                runOnUi(self.accountSearchBtn.config,state='normal')
                runOnUi(self.characSearchBtn.config,state='normal')
                #self.connectorE.config(values=[f'{i}-'+str(connector['account_db']) for i,connector in enumerate(sqlM.connectorAvailuableDictList)])
                runOnUi(self.connectorE.config,values=[f'{i}-'+str(connector) for i,connector in enumerate(sqlM.connectorAvailuableList)])
                #self.connectorE.set(f"0-{sqlM.connectorAvailuableDictList[0]['account_db']}")
                runOnUi(self.connectorE.set,f"0-{sqlM.connectorAvailuableList[0]}")
                onlineCharacs = sqlM.get_online_charac()
                runOnUi(self.fillCharac,onlineCharacs)
                print(f'当前在线角色已加载({len(onlineCharacs)})')
                runOnUi(self.update_event_list_func)
                self.refill_baned_tree()
                runOnUi(self.db_conBTN.config,text='重新连接',state='normal')
            print(sqlresult)
            self.password = pwd
            
            runOnUi(self.db_pwdE.delete,0,tk.END)
            
            runOnUi(self.db_pwdE.insert,0,'******')
            runOnUi(CreateToolTip,self.db_conBTN,'重新连接数据库并加载在线角色列表')

            self.fill_db_bak()
            self.sqlUserManageF.get_all_users()
            self.CONNECTING_FLG = False
            
        #if self.CONNECTING_FLG == False:
        self.db_conBTN.config(state='disable')
        self.CONNECTING_FLG = True
        print('正在连接数据库...')
        t = threading.Thread(target=inner)
        t.start()

