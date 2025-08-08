
from info2soft import config
from info2soft import https


class ActiveNodeCluster (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * Active集群 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listActiveNodeCluster(self, body):
        
        url = '{0}/active/node_cluster'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Active集群 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createActiveNodeCluster(self, body):
        
        url = '{0}/active/node_cluster'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Active集群 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def getActiveNodeClusterInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/node_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Active集群 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyActiveNodeCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/node_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Active集群 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteActiveNodeCluster(self, body):
        
        url = '{0}/active/node_cluster'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * Active集群 - 获取所有节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listClusterActiveNode(self, body):
        
        url = '{0}/active/node_cluster/nodes'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Active集群 - 新增节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addNodeActiveNodeCluster(self, body):
        
        url = '{0}/active/node_cluster/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Active集群 - 移除节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def removeNodeActiveNodeCluster(self, body):
        
        url = '{0}/active/node_cluster/node'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * Active集群 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listActiveNodeClusterStatus(self, body):
        
        url = '{0}/active/node_cluster/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Active集群 - 维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchAdtiveNodeClusterMaintenance(self, body):
        
        url = '{0}/active/node_cluster/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

