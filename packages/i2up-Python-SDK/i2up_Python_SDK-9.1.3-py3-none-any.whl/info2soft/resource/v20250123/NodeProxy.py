
from info2soft import config
from info2soft import https


class NodeProxy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 节点代理 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNodeProxy(self, body):
        
        url = '{0}/node_proxy'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点代理 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeProxy(self, body):
        
        url = '{0}/node_proxy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点代理 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeNodeProxy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/node_proxy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 节点代理 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNodeProxy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/node_proxy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 节点代理 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNodeProxy(self, body):
        
        url = '{0}/node_proxy'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

