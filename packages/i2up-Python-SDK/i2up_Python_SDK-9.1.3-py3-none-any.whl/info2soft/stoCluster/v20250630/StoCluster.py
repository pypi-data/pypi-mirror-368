
from info2soft import config
from info2soft import https


class StoCluster (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDedupeStorageCluster(self, body):
        
        url = '{0}/vers/v3/dedupe_storage_cluster'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDedupeStorageCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dedupe_storage_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDedupeStorageCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dedupe_storage_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDedupeStorageCluster(self, body):
        
        url = '{0}/vers/v3/dedupe_storage_cluster'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDedupeStorageCluster(self, body):
        
        url = '{0}/vers/v3/dedupe_storage_cluster'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDedupeStorageClusterStatus(self, body):
        
        url = '{0}/vers/v3/dedupe_storage_cluster/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

