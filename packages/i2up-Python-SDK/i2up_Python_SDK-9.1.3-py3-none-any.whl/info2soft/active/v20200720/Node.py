
from info2soft import config
from info2soft import https


class Node (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 未激活节点列表
     * 
     * @return list
    '''
    def listInactiveNodes(self, ):
        
        url = '{0}/active/node/inactive_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 节点列表(搜索)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodes(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/active/node/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNode(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/node/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 激活
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 节点升级
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upgradeNode(self, body):
        
        url = '{0}/active/node/upgrade'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点调试信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNodeDebugInfo(self, body):
        
        url = '{0}/active/node/debug_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

