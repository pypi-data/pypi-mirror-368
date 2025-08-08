
from info2soft import config
from info2soft import https


class Cfs (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCfs(self, body):
        
        url = '{0}/cfs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfs(self, body):
        
        url = '{0}/cfs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCfs(self, body):
        
        url = '{0}/cfs'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsStatus(self, body):
        
        url = '{0}/cfs/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def maintainCfs(self, body):
        
        url = '{0}/cfs/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 验证连接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def testConnect(self, body):
        
        url = '{0}/cfs/test_connect'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取集群可用区、文件系统列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsZoneFs(self, body):
        
        url = '{0}/cfs/list_zone_fs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

