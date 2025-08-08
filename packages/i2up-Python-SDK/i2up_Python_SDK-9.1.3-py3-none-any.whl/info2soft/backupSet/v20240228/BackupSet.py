
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
     * 备份集管理 - 操作 延长期限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def extendBackupSet(self, body):
        if body is None:
            body = {
                'operate': 'extend'
            }
        else:
            body['operate'] = 'extend'

        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作 延长期限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def expireBackupSet(self, body):
        if body is None:
            body = {
                'operate': 'expire'
            }
        else:
            body['operate'] = 'expire'

        url = '{0}/backup_set/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 操作 延长期限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def setPrimaryBackupSet(self, body):
        if body is None:
            body = {
                'operate': 'set_primary'
            }
        else:
            body['operate'] = 'set_primary'

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
     * 备份集管理 - 标记删除（底层程序调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupSet(self, body):
        
        url = '{0}/backup_set/delete'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集管理 - 删除失效备份集（底层程序调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupSetFromDb(self, body):
        
        url = '{0}/backup_set/delete_bk_set'.format(config.get_default('default_api_host'))
        
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
     * 备份集管理 - 查看备份链
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupChain(self, body):
        
        url = '{0}/backup_set/backup_chain'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

