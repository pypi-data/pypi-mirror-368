
from info2soft import config
from info2soft import https


class DiskPool (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 磁盘池 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDiskPool(self, body):
        
        url = '{0}/disk_pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁盘池 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDiskPool(self, body):
        
        url = '{0}/disk_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁盘池 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDiskPool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/disk_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 磁盘池 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDiskPool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/disk_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 磁盘池 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDiskPool(self, body):
        
        url = '{0}/disk_pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 磁盘池 - 检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkDiskPool(self, body):
        
        url = '{0}/disk_pool/check'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

