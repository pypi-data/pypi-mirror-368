
from info2soft import config
from info2soft import https


class FullMachineCopy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 整机副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机副本 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFullMachineCopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/full_machine_copy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 整机副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 整机副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFullMachineCopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/full_machine_copy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机副本 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFullMachineCopyStatus(self, body):
        
        url = '{0}/full_machine_copy/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机副本 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

