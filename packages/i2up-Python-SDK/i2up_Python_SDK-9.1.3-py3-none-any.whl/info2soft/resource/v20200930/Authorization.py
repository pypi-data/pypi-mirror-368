
from info2soft import config
from info2soft import https


class Authorization (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 资源授权 - 用户列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ListAuthorizationUser(self, body):

        url = '{0}/authorization/user'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源授权 - 用户授权情况
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getAuthorizationUserBind(self, body):
        
        url = '{0}/authorization/user_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源授权 - 更新用户授权
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateAuthorizationUserBind(self, body):
        
        url = '{0}/authorization/user_bind'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 资源授权 - 资源授权情况
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getAuthorizationResBind(self, body):
        
        url = '{0}/authorization/res_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源授权 - 更新资源授权
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateAuthorizationResBind(self, body):
        
        url = '{0}/authorization/res_bind'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 资源授权-获取绑定
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getAuthorizationBind(self, body):
        
        url = '{0}/authorization/bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源授权-更新绑定
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateAuthorizationBind(self, body):
        
        url = '{0}/authorization/bind'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

