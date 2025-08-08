
from info2soft import config
from info2soft import https


class CBG (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 激活授权码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activateAuthCode(self, body):
        
        url = '{0}/lic/activate_auth_code'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

