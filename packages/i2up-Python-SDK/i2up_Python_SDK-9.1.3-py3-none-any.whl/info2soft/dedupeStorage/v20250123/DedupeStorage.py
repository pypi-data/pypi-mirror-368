
from info2soft import config
from info2soft import https


class DedupeStorage (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDedupeStorage(self, body):
        
        url = '{0}/vers/v3/dedupe_storage'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDedupeStorage(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dedupe_storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDedupeStorage(self, body):
        
        url = '{0}/vers/v3/dedupe_storage'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDedupeStorage(self, body):
        
        url = '{0}/vers/v3/dedupe_storage'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDedupeStorage(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dedupe_storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDedupeStorageStatus(self, body):
        
        url = '{0}/vers/v3/dedupe_storage/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoverSpaceDedupeStorage(self, body):
        
        url = '{0}/vers/v3/dedupe_storage/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取备份服务器重删存储已使用端口列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBkSvrUsedPorts(self, body):
        
        url = '{0}/vers/v3/dedupe_storage/list_bk_used_port'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

