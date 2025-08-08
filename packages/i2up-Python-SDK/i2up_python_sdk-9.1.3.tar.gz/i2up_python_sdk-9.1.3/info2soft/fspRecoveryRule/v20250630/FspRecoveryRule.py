
from info2soft import config
from info2soft import https


class FspRecoveryRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 整机恢复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryRules(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listFspRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/fsp/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机恢复 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFspRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/fsp/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebootFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def powerOnFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def powerOffFspRecoveryRule(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryRuleStatus(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 获取BIOS类型
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getFspRecoveryRuleBiosType(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/bios_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机恢复 - 目标机驱动URL列表
     * 
     * @return list
    '''
    def listFspRecoveryRuleDriverListUrl(self, body):
        
        url = '{0}/vers/v3/fsp/recovery_rule/driver_url_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

