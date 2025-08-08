
from info2soft import config
from info2soft import https


class DtoStorageBucket (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoStorageBucket(self, body):
        
        url = '{0}/dto/storage_bucket'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtoStorageBucket(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/storage_bucket/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoStorageBucket(self, body):
        
        url = '{0}/dto/storage_bucket'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoStorageBucket(self, body):
        
        url = '{0}/dto/storage_bucket'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 批量导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importDtoStorageBucket(self, body):
        
        url = '{0}/dto/storage_bucket/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

