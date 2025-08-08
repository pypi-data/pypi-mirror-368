
from info2soft import config
from info2soft import https


class RepBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 复制规则 - 获取 cdp zfs池列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupCdpZfs(self, body):
        
        url = '{0}/rep/backup/cdp_zfs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 检查是否挂载盘
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def repBackupVerifyDevice(self, body):
        
        url = '{0}/rep/backup/verify_device'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 复制规则 - 获取可配置CDP快照数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getRepBackupCdpSnapNum(self, body):
        
        url = '{0}/rep/backup/cdp_snap_num'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRepBackup(self, body):
        
        url = '{0}/rep/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 复制规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRepBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 复制规则 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRepBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 复制规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRepBackup(self, body):
        
        url = '{0}/rep/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 复制规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupStatus(self, body):
        
        url = '{0}/rep/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackup(self, body):
        
        url = '{0}/rep/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - cdp baseline 列表 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupBaseLine(self, body):
        
        url = '{0}/rep/backup/cdp_bl_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - cdp baseline 列表 删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRepBackupBaseline(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/cdp_bl_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 复制规则 - 孤儿文件 列表 获取
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupOrphan(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/orphan_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 孤儿文件 列表 删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRepBackupOrphan(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/orphan_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 复制规则 - 孤儿文件 下载
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadRepBackupOrphan(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/orphan_download'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 快照 列表 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupSnapshot(self, body):
        
        url = '{0}/rep/backup/snapshot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 快照 创建
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def createRepBackupSnapshot(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/snapshot_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, None, self.auth)
        return res

    '''
     * 复制规则 - 快照 删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRepBackupSnapshot(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/backup/{1}/snapshot_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 复制规则 - 获取集群组信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepBackupMscsGroup(self, body):
        
        url = '{0}/rep/backup/mscs_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 5 Dashboard - 获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def repBackup(self, body):
        
        url = '{0}/dashboard/rep'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateRepBackup(self, body):
        
        url = '{0}/rep/backup/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 复制规则 - 检查目标路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkBkPath(self, body):
        
        url = '{0}/rep/backup/check_bk_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 复制规则 - 提交前检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def chkRules(self, body):
        
        url = '{0}/rep/backup/rules_chk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

