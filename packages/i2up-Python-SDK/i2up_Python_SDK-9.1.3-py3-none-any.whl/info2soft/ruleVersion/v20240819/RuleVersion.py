
from info2soft import config
from info2soft import https


class RuleVersion (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 历史版本 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleVersion(self, body):
        
        url = '{0}/rule_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 历史版本 - 查看具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleVersionInfo(self, body):
        
        url = '{0}/rule_version/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 历史版本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def setMainRuleVersion(self, body):
        
        url = '{0}/rule_version/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

