
from info2soft import config
from info2soft import https


class Statistics (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 事件记录 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatistics(self, body):
        
        url = '{0}/statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 事件记录 - 单条详情
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def describeStatistics(self, body, id):
        if id is None:
            exit()
        url = '{0}/statistics/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 事件记录 - 标为已读
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def readStatistics(self, body):
        
        url = '{0}/statistics'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 事件统计 - 整体统计 - 按功能统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatisticsChart(self, body):
        
        url = '{0}/statistics/chart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 统计报表 - 发送配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateStatisticsConfig(self, body):
        
        url = '{0}/statistics/config'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 统计报表 - 获取配置信息
     * 
     * @return list
    '''
    def listStatisticsConfig(self, body):
        
        url = '{0}/statistics/config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 事件记录 - 下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadStatistics(self, body):
        
        url = '{0}/statistics/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 事件统计 - 整体统计下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadStatisticsChart(self, body):
        
        url = '{0}/statistics/chart_download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 事件统计 - 整体统计 - 按规则统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatisticsRuleChart(self, body):
        
        url = '{0}/statistics/rule_chart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 事件统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatisticsTrendChart(self, body):
        
        url = '{0}/statistics/trend_chart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

