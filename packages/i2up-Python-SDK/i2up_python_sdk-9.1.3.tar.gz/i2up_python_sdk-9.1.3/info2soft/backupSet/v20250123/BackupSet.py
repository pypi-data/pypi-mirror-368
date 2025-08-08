
from info2soft import config
from info2soft import https


class BackupSet (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份集管理 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupSet(self, body):
        
        url = '{0}/backup_set'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 获取列表查询候选信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQueryArgsBackupSet(self, body):
        
        url = '{0}/backup_set/query_args'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def extendBackupSet(self, body):
        
        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def expireBackupSet(self, body):
        
        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def setPrimaryBackupSet(self, body):
        
        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def mountBackupSet(self, body):
        
        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def unmountBackupSet(self, body):
        
        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 手动删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDbBackupSet(self, body):
        
        url = '{0}/backup_set'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 手动强制清理
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def manualForceDeleteDbBackupSet(self, body):
        
        url = '{0}/backup_set/force_delete'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 标记删除（内部程序调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupSet(self, body):
        
        url = '{0}/backup_set/delete'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集复制 - 提交复制规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackupSetRepRule(self, body):
        
        url = '{0}/backup_set/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 单个
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBackupSet(self, body):
        
        url = '{0}/backup_set/single'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 已删除备份集 单个
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDeletedBackupSet(self, body):
        
        url = '{0}/backup_set/single_deleted'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 查看副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBackupSetCopy(self, body):
        
        url = '{0}/backup_set/copy_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集复制 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupSetRule(self, body):
        
        url = '{0}/backup_set/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 验证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def validateBackupSet(self, body):
        
        url = '{0}/backup_set/verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 过期当前主副本 & 更新最小副本号备份集为主副本（内部程序调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetPrimaryBackupSet(self, body):
        
        url = '{0}/backup_set/reset_primary'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 查看备份链
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupChain(self, body):
        
        url = '{0}/backup_set/backup_chain'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 演练
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def drillBackupSet(self, body):
        
        url = '{0}/backup_set/drill'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取（存在备份集的）实例客户端列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSrcClient(self, body):
        
        url = '{0}/backup_set/list_src_client'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 介质验证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def validationBackupSet(self, body):
        
        url = '{0}/backup_set/validation'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 获取介质验证结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getValidationResult(self, body):
        
        url = '{0}/backup_set/validation_result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

