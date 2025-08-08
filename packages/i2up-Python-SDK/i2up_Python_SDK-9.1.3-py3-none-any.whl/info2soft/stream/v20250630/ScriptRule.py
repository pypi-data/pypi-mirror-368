
from info2soft import config
from info2soft import https


class ScriptRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 执行管理 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRule(self, body):
        
        url = '{0}/vers/v3/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 执行管理 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRule(self, body):
        
        url = '{0}/vers/v3/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 执行管理 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRules(self, body):
        
        url = '{0}/vers/v3/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 执行管理 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/script_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 执行管理 - 结果
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def getScriptRuleResultDetail(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/script_rule/status_detail/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 执行管理 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleStatus(self, body):
        
        url = '{0}/vers/v3/mask/script_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 执行管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startRule(self, body):
        
        url = '{0}/vers/v3/mask/script_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 执行管理 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRule(self, body):
        
        url = '{0}/vers/v3/mask/script_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

