
from info2soft import config
from info2soft import https


class First (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 一级副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFirstReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/first/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 一级副本 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFirstReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/first/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFirstReplicaStatus(self, body):
        
        url = '{0}/replica/first/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 一级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmFirstReplica(self, body):
        
        url = '{0}/replica/first/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmFirstReplica(self, body):
        
        url = '{0}/replica/first/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

