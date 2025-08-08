
from info2soft import config
from info2soft import https


class BackupRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackup(self, body):
        
        url = '{0}/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份规则 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份规则 - 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份规则 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupRule(self, body):
        
        url = '{0}/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupRule(self, body):
        
        url = '{0}/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableBackupRule(self, body):
        
        url = '{0}/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def disableBackupRule(self, body):
        
        url = '{0}/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def manualStartBackupRule(self, body):
        
        url = '{0}/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cloneBackupRule(self, body):
        
        url = '{0}/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份规则 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupRuleStatus(self, body):
        
        url = '{0}/backup_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份规则 - NBU备份清理临时数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cleanNbuCache(self, body):
        
        url = '{0}/backup_rule/clean_nbu_cache'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Oracle备份 - 获取脚本路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeScriptPath(self, body):
        
        url = '{0}/backup_rule/script_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

