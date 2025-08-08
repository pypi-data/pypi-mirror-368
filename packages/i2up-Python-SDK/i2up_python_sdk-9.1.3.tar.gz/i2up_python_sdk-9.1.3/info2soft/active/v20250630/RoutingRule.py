
from info2soft import config
from info2soft import https


class RoutingRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 巡检规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createReportRule(self, body):
        
        url = '{0}/stream_routing'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyReportRule(self, body):
        
        url = '{0}/stream_routing'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRule(self, body):
        
        url = '{0}/stream_routing'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRuleStatus(self, body):
        
        url = '{0}/stream_routing/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteReportRule(self, body):
        
        url = '{0}/stream_routing'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateReportRule(self, body):
        
        url = '{0}/stream_routing/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 导出历史
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRuleHistory(self, body):
        
        url = '{0}/stream_routing/history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 更新巡检kafka推送配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStreamRoutingConf(self, body):
        
        url = '{0}/stream_routing/config'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 查看巡检kafka推送配置副本
     * 
     * @return list
    '''
    def listStreamRoutingConf(self, body):
        
        url = '{0}/stream_routing/config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 巡检规则 - 删除历史
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteReportRuleHistory(self, body):
        
        url = '{0}/stream_routing/history'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 获取巡检结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReportRuleResult(self, body):
        
        url = '{0}/stream_routing/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 巡检规则 - 获取资源
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBizGroupResource(self, body):
        
        url = '{0}/stream_routing/get_rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

