
from info2soft import config
from info2soft import https


class VmCloneRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 虚机克隆规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVmCloneRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机克隆规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneRuleStatus(self, body):
        
        url = '{0}/vm_clone/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

