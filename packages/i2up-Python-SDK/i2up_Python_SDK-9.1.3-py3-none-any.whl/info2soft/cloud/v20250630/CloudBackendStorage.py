
from info2soft import config
from info2soft import https


class CloudBackendStorage (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 后端存储列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackendStorages(self, body):
        
        url = '{0}/cloud/backend_storage'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 后端存储，获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBackendStorage(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/backend_storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建后端存储
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackendStorage(self, body):
        
        url = '{0}/cloud/backend_storage'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改后端存储
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBackendStorage(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/backend_storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除后端存储
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackendStorage(self, body):
        
        url = '{0}/cloud/backend_storage'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

