
from info2soft import config
from info2soft import https


class OracleReverse (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 反向规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createReverse(self, body):
        
        url = '{0}/vers/v3/sync_reverse'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

