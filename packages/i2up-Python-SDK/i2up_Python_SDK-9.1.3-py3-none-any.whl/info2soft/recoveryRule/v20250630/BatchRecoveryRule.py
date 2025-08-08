
from info2soft import config
from info2soft import https


class BatchRecoveryRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 场景化恢复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRestoreWizardRuleStatus(self, body):
        
        url = '{0}/vers/v3/restore_wizard/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRestoreWizardRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/restore_wizard/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def regenerateRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restoreRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRestoreWizardRule(self, body):
        
        url = '{0}/vers/v3/restore_wizard'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 下载清单文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadRestoreWizardList(self, body):
        
        url = '{0}/vers/v3/restore_wizard/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 场景化恢复 - 查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRestoreWizardRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/restore_wizard/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

