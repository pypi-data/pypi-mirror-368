
from info2soft import config
from info2soft import https


class StorageUnit (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 存储单元 - 准备(查看容量)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getStorageUnitBkCapacity(self, body):
        
        url = '{0}/storage_unit/capacity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元 - 获取驱动数量
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getStorageUnitDrivers(self, body):
        
        url = '{0}/storage_unit/drivers'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStorageUnit(self, body):
        
        url = '{0}/storage_unit'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储单元 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStorageUnit(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_unit/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 存储单元 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeStorageUnit(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_unit/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 存储单元 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageUnit(self, body):
        
        url = '{0}/storage_unit'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStorageUnit(self, body):
        
        url = '{0}/storage_unit'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 存储单元 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageUnitStatus(self, body):
        
        url = '{0}/storage_unit/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元 - 提交前检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def chkStorageUnitRules(self, body):
        
        url = '{0}/storage_unit/rules_chk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元组 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStorageUnitGroup(self, body):
        
        url = '{0}/storage_unit_group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储单元组 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStorageUnitGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_unit_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 存储单元组 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeStorageUnitGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage_unit_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 存储单元组 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageUnitGroup(self, body):
        
        url = '{0}/storage_unit_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储单元组 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStorageUnitGroup(self, body):
        
        url = '{0}/storage_unit_group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 存储单元 - 可用并发数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getStorageUnitAvailableConcurrent(self, body):
        
        url = '{0}/storage_unit/available_concurrent'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

