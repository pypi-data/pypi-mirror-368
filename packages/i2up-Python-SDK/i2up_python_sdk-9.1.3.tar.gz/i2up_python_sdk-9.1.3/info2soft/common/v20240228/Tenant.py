from info2soft import config
from info2soft import https


class Tenant(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTenant(self, body):
        url = '{0}/tenant'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createTenant(self, body):
        url = '{0}/tenant'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def modifyTenant(self, body, num):
        url = '{0}/tenant/{1}'.format(config.get_default('default_api_host'), num)

        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteTenant(self, body):
        url = '{0}/tenant'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

