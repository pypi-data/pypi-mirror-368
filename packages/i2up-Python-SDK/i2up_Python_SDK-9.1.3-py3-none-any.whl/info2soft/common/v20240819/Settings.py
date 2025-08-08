
from info2soft import config
from info2soft import https


class Settings (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 系统设置-获取配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSysSetting(self, body):
        
        url = '{0}/sys/settings'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 系统设置-更新配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSetting(self, body):
        
        url = '{0}/sys/settings'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 系统设置-更新安全配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSecuritySetting(self, body):
        
        url = '{0}/sys/settings/security_settings'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 系统设置-更新消息推送配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateNotifySetting(self, body):
        
        url = '{0}/sys/settings/notify_settings'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 系统设置-获取公开配置
     * 
     * @return list
    '''
    def listPublicSettings(self, body):
        
        url = '{0}/sys/public_settings'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 系统设置-控制台主机IP
     * 
     * @return list
    '''
    def describeCCip(self, body):
        
        url = '{0}/sys/settings/ips'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 更新节点参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateNodeConf(self, body):
        
        url = '{0}/sys/settings/node_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取节点参数
     * 
     * @return list
    '''
    def listNodeConf(self, body):
        
        url = '{0}/sys/settings/node_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 用户管理(admin)-新增用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户管理(admin)-用户列表(admin)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 用户管理(admin)-获取用户
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def describeUser(self, body, id):
        if id is None:
            exit()
        url = '{0}/user/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 用户管理(admin)-删除账户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 用户管理(admin)-修改用户信息
     * 
     * @body['id'] String  必填 id
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUser(self, body, id):
        if id is None:
            exit()
        url = '{0}/user/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户管理 - 解除用户登录锁定
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def clearLoginAttempt(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/user/{1}/clear_login_attempt'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户 - 手机号/邮箱 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUserEmailOrMobile(self, body):
        
        url = '{0}/user/email_mobile'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户Profile(all user)-修改密码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUserPwd(self, body):
        
        url = '{0}/user/password'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户Profile(all user)-获取用户Profile
     * 
     * @return list
    '''
    def listProfile(self, body):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 用户修改个人资料
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyProfile(self, body):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户修改消息推送地址
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUserNotifyAddr(self, body):
        
        url = '{0}/user/notify_addr'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户Profile(all user)-退出登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def logout(self, body):
        
        url = '{0}/user/logout'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * AccessKey列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * AccessKey新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * AccessKey更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * AccessKey删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 角色管理 - 角色列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRole(self, body):
        
        url = '{0}/role'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNpsvr(self, body):
        
        url = '{0}/cc/npsvr_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr获取单个
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeNpsvr(self, body):
        
        url = '{0}/cc/npsvr'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNpsvr(self, body):
        
        url = '{0}/cc/npsvr'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * npsvr删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNpsvr(self, body):
        
        url = '{0}/cc/npsvr'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * npsvr状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNpsvrStatus(self, body):
        
        url = '{0}/cc/npsvr_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr 备份历史列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNpsvrBakList(self, body):
        
        url = '{0}/cc/npsvr_bak_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr 备份历史操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryNpsvrBak(self, body):
        
        url = '{0}/cc/npsvr_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * npsvr 备份历史操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNpsvrBak(self, body):
        
        url = '{0}/cc/npsvr_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置备份 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakConfig(self, body):
        
        url = '{0}/cc/bak_config_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置备份 - 单个
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBakConfig(self, body):
        
        url = '{0}/cc/bak_config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置备份 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBakConfig(self, body):
        
        url = '{0}/cc/bak_config'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 配置备份 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBakConfig(self, body):
        
        url = '{0}/cc/bak_config'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 配置备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakConfigStatus(self, body):
        
        url = '{0}/cc/bak_config_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置备份 - 获取备份历史列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakHistory(self, body):
        
        url = '{0}/cc/bak_history_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置备份-导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importConfig(self, body):
        
        url = '{0}/cc/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置备份-导出
     * 
     * @return list
    '''
    def exportConfig(self, body):
        
        url = '{0}/cc/export'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置备份 - 备份历史操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryBakConfigInfo(self, body):
        
        url = '{0}/cc/bak_history_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置备份 - 备份历史操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBakConfigInfo(self, body):
        
        url = '{0}/cc/bak_history_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置备份 - 获取Ctrl备份配置
     * 
     * @return list
    '''
    def describeCtrlBakSetting(self, body):
        
        url = '{0}/cc/bak_setting'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 配置备份 - 修改Ctrl备份配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCtrlBakSetting(self, body):
        
        url = '{0}/cc/bak_setting'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 查看音频文件
     * 
     * @return list
    '''
    def listDownloadCustomAudio(self, body):
        
        url = '{0}/sys/settings/custom_audio_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 上传音频文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadDownloadCustomAudio(self, body):
        
        url = '{0}/sys/settings/custom_audio'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除音频文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDownloadCustomAudio(self, body):
        
        url = '{0}/sys/settings/custom_audio'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 下载音频文件
     * 
     * @return list
    '''
    def downloadCustomAudio(self, body):
        
        url = '{0}/sys/settings/custom_audio'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * etcd有效性检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def chkEtcdUrl(self, body):
        
        url = '{0}/etcd/etcd_url_chk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务调度器 - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUpdateScheduleSvr(self, body):
        
        url = '{0}/schedule_svr'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 服务调度器 - 列表
     * 
     * @return list
    '''
    def listScheduleSvr(self, body):
        
        url = '{0}/schedule_svr'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * ETCD - 发现
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanEtcdConf(self, body):
        
        url = '{0}/etcd/scan'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ETCD - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUpdateEtcd(self, body):
        
        url = '{0}/etcd'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ETCD - 列表
     * 
     * @return list
    '''
    def listEtcd(self, body):
        
        url = '{0}/etcd'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 错误代码 - 列表
     * 
     * @return list
    '''
    def listErrorCode(self, body):
        
        url = '{0}/cc/error_code'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

