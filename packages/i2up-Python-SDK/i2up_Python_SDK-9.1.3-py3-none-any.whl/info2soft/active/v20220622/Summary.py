
from info2soft import config
from info2soft import https


class Summary (object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 获取总览列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryView(self, body):
        
        url = '{0}/active/summary/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 总览页面
     * 
     * @return list
    '''
    def listSummary(self, body):

        url = '{0}/active/summary'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 测试-总览拓补图
     * 
     * @return list
    '''
    def listSummaryChart(self, body):

        url = '{0}/active/summary/chart'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

