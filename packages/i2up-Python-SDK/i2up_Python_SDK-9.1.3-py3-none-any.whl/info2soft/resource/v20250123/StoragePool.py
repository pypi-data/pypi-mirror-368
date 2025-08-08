
from info2soft import config
from info2soft import https


class StoragePool (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 扫描，获取存储机可用磁盘列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def availablePoolMemberList(self, body):
        
        url = '{0}/storage_pool/available_pool_member'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新建存储池
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStoragePool(self, body):
        
        url = '{0}/storage_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改存储池
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStoragePool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 查看列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def storagePoolList(self, body):
        
        url = '{0}/storage_pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeStoragePool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStoragePool(self, body):
        
        url = '{0}/storage_pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStoragePoolStatus(self, body):
        
        url = '{0}/storage_pool/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取 fc 目标端 hba卡信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHbaInfo(self, body):
        
        url = '{0}/storage_pool/hba_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除fc_target
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFcTarget(self, body):
        
        url = '{0}/storage_pool/fc_target'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 存储池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetStoragePool(self, body):
        
        url = '{0}/storage_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def extendStoragePool(self, body):
        
        url = '{0}/storage_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def renewKeyStoragePool(self, body):
        
        url = '{0}/storage_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取节点存储池列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def storagePoolLoadPools(self, body):
        
        url = '{0}/storage_pool/load_pools'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量导入存储池
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def storagePoolBatchImport(self, body):
        
        url = '{0}/storage_pool/batch_import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储池 - 更新配置项
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def storagePoolUpdateConfig(self, body):
        
        url = '{0}/storage_pool/update_config'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

