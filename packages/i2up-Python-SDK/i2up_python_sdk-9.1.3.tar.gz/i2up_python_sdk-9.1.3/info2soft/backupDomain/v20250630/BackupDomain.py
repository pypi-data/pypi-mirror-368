
from info2soft import config
from info2soft import https


class BackupDomain (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份域 - 获取目标域存储单元列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTargetDomainStorageUnit(self, body):
        
        url = '{0}/backup_domain/storage_unit'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份域 - 获取目标域存储单元状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTargetDomainStorageUnitStatus(self, body):
        
        url = '{0}/backup_domain/storage_unit_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份域 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackupDomain(self, body):
        
        url = '{0}/backup_domain'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份域 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBackupDomain(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_domain/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份域 - 认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authBackupDomain(self, body):
        
        url = '{0}/backup_domain/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份域 - 列表
     * 
     * @return list
    '''
    def listBackupDomain(self, body):
        
        url = '{0}/backup_domain'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份域 - 单个查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBackupDomain(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_domain/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份域 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupDomain(self, body):
        
        url = '{0}/backup_domain'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

