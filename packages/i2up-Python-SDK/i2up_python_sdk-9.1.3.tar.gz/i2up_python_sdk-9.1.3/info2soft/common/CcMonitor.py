
from info2soft import config
from info2soft import https


class CcMonitor (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 主界面
     * 
     * @return list
    '''
    def listCcMonitor(self, body):
        
        url = '{0}/cc_monitor'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 单个节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/cc_monitor/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

