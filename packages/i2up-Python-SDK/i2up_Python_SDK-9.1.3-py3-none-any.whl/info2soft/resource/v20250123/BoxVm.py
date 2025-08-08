
from info2soft import config
from info2soft import https


class BoxVm (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 虚机 - 获取模板列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def templateList(self, body):
        
        url = '{0}/box_vm/template'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBoxVm(self, body):
        
        url = '{0}/box_vm'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def boxVmList(self, body):
        
        url = '{0}/box_vm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBoxVm(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/box_vm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBoxVm(self, body):
        
        url = '{0}/box_vm'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBoxVmStatus(self, body):
        
        url = '{0}/box_vm/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerBoxVm(self, body):
        
        url = '{0}/box_vm/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

