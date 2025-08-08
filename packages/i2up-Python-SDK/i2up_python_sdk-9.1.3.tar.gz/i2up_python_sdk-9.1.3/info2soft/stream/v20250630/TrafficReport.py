
from info2soft import config
from info2soft import https


class TrafficReport (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 报表规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRule(self, body):
        
        url = '{0}/vers/v3/report_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 报表规则 - 查看报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRuleStatistics(self, body):
        
        url = '{0}/vers/v3/report_rule/statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 报表规则 - 导出历史
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRuleHistory(self, body):
        
        url = '{0}/vers/v3/report_rule/history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

