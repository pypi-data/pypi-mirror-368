
from info2soft import config
from info2soft import https


class RuleMonitor (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 监控统计 - 机器节点折线图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listActiveNodeChart(self, body):
        
        url = '{0}/stream/resource/node_chart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 监控统计 - 机器节点资源占用
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listActiveNodeResources(self, body):
        
        url = '{0}/stream/resource/node_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 监控统计 - 设置机器节点默认监控路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateNodeDefaultMonitorPath(self, body):
        
        url = '{0}/stream/resource/node_path'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取监控配置
     * 
     * @return list
    '''
    def getSyncRuleMonitorConf(self, body):
        
        url = '{0}/vers/v3/stream/monitor'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 更新监控配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySyncRuleMonitorConf(self, body):
        
        url = '{0}/vers/v3/stream/monitor'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 监控信息导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportSyncRuleMonitorStat(self, body):
        
        url = '{0}/active/rule/statistics_export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 规则状态监控 解析统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRuleExtractStatistics(self, body):
        
        url = '{0}/active/rule/extract_statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 规则状态监控 装载统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRuleLoadStatistics(self, body):
        
        url = '{0}/active/rule/load_statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 规则状态监控 表解析统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRuleTableExtractStatistics(self, body):
        
        url = '{0}/active/rule/table_extract_statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 规则状态监控 表装载统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRuleTableLoadStatistics(self, body):
        
        url = '{0}/active/rule/table_load_statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

