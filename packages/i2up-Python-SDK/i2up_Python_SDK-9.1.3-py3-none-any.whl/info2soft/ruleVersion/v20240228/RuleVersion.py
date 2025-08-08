
from info2soft import config
from info2soft import https


class RuleVersion (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取规则历史版本列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleVersion(self, body):
        
        url = '{0}/rule_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看具体配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleVersionInfo(self, body):
        
        url = '{0}/rule_version/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

