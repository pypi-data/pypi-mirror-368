
from info2soft import config
from info2soft import https


class Second (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 二级副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 二级副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeSecondReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/second/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 二级副本 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startSecondReplica(self, body):
        
        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSecondReplica(self, body):
        
        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmSecondReplica(self, body):
        
        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmSecondReplica(self, body):
        
        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 二级副本 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecondReplicaStatus(self, body):
        
        url = '{0}/replica/second/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

