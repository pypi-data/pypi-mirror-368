
from info2soft import config
from info2soft import https


class Recovery (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取接管列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryList(self, body):
        
        url = '{0}/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取接管规则状态（工作机、上次运行时间、回切）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryStatus(self, body):
        
        url = '{0}/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

