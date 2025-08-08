
from info2soft import config
from info2soft import https


class VmCloneVm (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 虚机克隆虚机 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneVm(self, body):
        
        url = '{0}/vm_clone/vm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 修改虚机配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVmConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/vm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVmCloneVm(self, body):
        
        url = '{0}/vm_clone/vm'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmVmCloneVm(self, body):
        
        url = '{0}/vm_clone/vm/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmVmCloneVm(self, body):
        
        url = '{0}/vm_clone/vm/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneVmStatus(self, body):
        
        url = '{0}/vm_clone/vm/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVmCloneVm(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/vm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

