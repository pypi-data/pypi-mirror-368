
from info2soft import config
from info2soft import https


class MaskRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 数据安全总览
     * 
     * @return list
    '''
    def listSummary(self, body):
        
        url = '{0}/vers/v3/mask/summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 数据安全总览 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryView(self, body):
        
        url = '{0}/vers/v3/mask/summary/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMaskRules(self, body):
        
        url = '{0}/vers/v3/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMaskRules(self, body):
        
        url = '{0}/vers/v3/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startMaskRule(self, body):
        
        url = '{0}/vers/v3/mask/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopMaskRule(self, body):
        
        url = '{0}/vers/v3/mask/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMaskRule(self, body):
        
        url = '{0}/vers/v3/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeMaskRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 脱敏规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMaskRuleStatus(self, body):
        
        url = '{0}/vers/v3/mask/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 导入脱敏文件配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importMaskRuleInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/rule/import_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

