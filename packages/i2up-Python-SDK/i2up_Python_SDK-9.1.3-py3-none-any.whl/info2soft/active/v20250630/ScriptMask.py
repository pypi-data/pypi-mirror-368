
from info2soft import config
from info2soft import https


class ScriptMask (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 增加脚本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createScript(self, body):
        
        url = '{0}/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改脚本
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyScript(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/script/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除脚本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteScript(self, body):
        
        url = '{0}/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取脚本列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listScript(self, body):
        
        url = '{0}/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 下载脚本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadScript(self, body):
        
        url = '{0}/mask/script/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取脚本详细信息
     * 
     * @body['id'] String  必填 id
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptScript(self, body, id):
        if id is None:
            exit()
        url = '{0}/mask/script/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 增加规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRule(self, body):
        
        url = '{0}/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 增加规则副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyScriptRule(self, body):
        
        url = '{0}/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRule(self, body):
        
        url = '{0}/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRules(self, body):
        
        url = '{0}/mask/script_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取规则详细信息
     * 
     * @body['id'] String  必填 id
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptRule(self, body, id):
        if id is None:
            exit()
        url = '{0}/mask/script_rule/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取脚本执行结果
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def getScriptRuleResultDetail(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/script_rule/status_detail/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取规则状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleStatus(self, body):
        
        url = '{0}/mask/script_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 启/停规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startRule(self, body):
        
        url = '{0}/mask/script_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 启/停规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRule(self, body):
        
        url = '{0}/mask/script_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

