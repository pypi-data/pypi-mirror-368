
from info2soft import config
from info2soft import https


class Node (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  【字段说明】
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def readme(self, body):
        
        url = '{0}/distribution/node/readme'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  注册（底层）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def register(self, body):
        
        url = '{0}/distribution/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  更新状态（底层）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateStatus(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}/status'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNode(self, body):
        
        url = '{0}/distribution/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/distribution/node/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取 节点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeNode(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  设置 文件
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def fileConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}/file_config'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  设置 警告
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def warnConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}/warn_config'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  升级
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upgrade(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}/upgrade'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def delete(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/distribution/node/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  拓扑图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def topography(self, body):
        
        url = '{0}/distribution/node/topography'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  延迟图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def latency(self, body):
        
        url = '{0}/distribution/node/latency'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

