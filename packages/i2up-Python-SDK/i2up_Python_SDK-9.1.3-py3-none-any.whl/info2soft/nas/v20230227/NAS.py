
from info2soft import config
from info2soft import https


class NAS (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * nas 同步 - 组 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNAS(self, body):
        
        url = '{0}/nas/sync'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * nas 同步 - 组 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeNASGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/nas/sync/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * nas 同步 - 组 编辑
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNAS(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/nas/sync/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * nas 同步 - 获取 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNAS(self, body):
        
        url = '{0}/nas/sync'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * nas 同步 - 获取 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNASStatus(self, body):
        
        url = '{0}/nas/sync/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * nas 同步 - 操作：启停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startNAS(self, body):
        
        url = '{0}/nas/sync/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * nas 同步 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNAS(self, body):
        
        url = '{0}/nas/sync'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

