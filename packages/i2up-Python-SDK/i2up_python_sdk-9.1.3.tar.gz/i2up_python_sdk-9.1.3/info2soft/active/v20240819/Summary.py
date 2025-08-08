
from info2soft import config
from info2soft import https


class Summary (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 总览 - 同步任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryView(self, body):
        
        url = '{0}/active/summary/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库同步 - 总览
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummary(self, body):
        
        url = '{0}/active/summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

