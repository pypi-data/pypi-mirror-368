
from info2soft import config
from info2soft import https


class AppContinuity (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 应用容灾 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAppContinuity(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_continuity/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeAppContinuity(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_continuity/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用容灾 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def mmediatelyAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def eleteAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failoverAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failbackAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def criptAppContinuity(self, body):
        
        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAppContinuityStatus(self, body):
        
        url = '{0}/app_continuity/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

