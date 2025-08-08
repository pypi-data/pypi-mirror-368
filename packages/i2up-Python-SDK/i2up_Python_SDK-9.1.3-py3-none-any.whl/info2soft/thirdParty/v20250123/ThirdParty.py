
from info2soft import config
from info2soft import https


class ThirdParty (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 第三方系统接入- 获取跳转url
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getThirdPartiesUrl(self, body):
        
        url = '{0}/third_parties/url'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

