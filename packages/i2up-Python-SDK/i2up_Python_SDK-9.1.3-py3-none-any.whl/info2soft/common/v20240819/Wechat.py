
from info2soft import config
from info2soft import https


class Wechat (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 用户 - 绑定微信
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def bindUser(self, body):
        
        url = '{0}/wechat/bind'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户 - 解绑微信
     * 
     * @return list
    '''
    def unbindUser(self, body):
        
        url = '{0}/wechat/unbind'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取用户绑定状态
     * 
     * @return list
    '''
    def bindStatus(self, body):
        
        url = '{0}/wechat/bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

