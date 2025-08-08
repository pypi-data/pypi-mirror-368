
from info2soft import config
from info2soft import https


class AppSystem (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取列表
     * 
     * @return list
    '''
    def secDirList(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSecDir(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySecDir(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/sec_dir/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSecDir(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def appSystemList(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取列表（附加成员列表）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def appSystemMembersList(self, body):
        
        url = '{0}/app_sys/get_app_sys_members'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeAppSystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_sys/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAppSystem(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAppSystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_sys/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAppSystem(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取虚机成员列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmList(self, body):
        
        url = '{0}/app_sys/vm_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看全部成员列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getMembersList(self, body):
        
        url = '{0}/app_sys/members_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动注册节点（底层调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def autoRegisterNode(self, body):
        
        url = '{0}/api/client/rest_rpc/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

