
from info2soft import config
from info2soft import https


class FspBackupRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 整机备份 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机备份 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机备份 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFspBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/fsp/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机备份 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFspBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/fsp/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 整机备份 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 整机备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def disableFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def manualStartFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cloneFspBackupRule(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupRuleStatus(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机备份 - 获取节点设备列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupDeviceInfo(self, body):
        
        url = '{0}/vers/v3/fsp/backup_rule/device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

