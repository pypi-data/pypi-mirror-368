
from info2soft import config
from info2soft import https


class Group (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNodeGroup(self, body):
        
        url = '{0}/distribution/node_group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeGroup(self, body):
        
        url = '{0}/distribution/node_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeNodeGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNodeGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNodeGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBlockGroup(self, body):
        
        url = '{0}/distribution/block_group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBlockGroup(self, body):
        
        url = '{0}/distribution/block_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBlockGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/block_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBlockGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/block_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBlockGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/block_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

