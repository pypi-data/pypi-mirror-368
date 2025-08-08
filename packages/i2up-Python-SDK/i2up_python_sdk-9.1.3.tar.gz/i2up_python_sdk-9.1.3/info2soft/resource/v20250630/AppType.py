
from info2soft import config
from info2soft import https


class AppType (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 应用类型 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAppType(self, body):
        
        url = '{0}/app_type'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用类型 - 列表
     * 
     * @return list
    '''
    def listAppType(self, body):
        
        url = '{0}/app_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用类型 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeAppType(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_type/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用类型 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAppType(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_type/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 应用类型 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAppType(self, body):
        
        url = '{0}/app_type'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

