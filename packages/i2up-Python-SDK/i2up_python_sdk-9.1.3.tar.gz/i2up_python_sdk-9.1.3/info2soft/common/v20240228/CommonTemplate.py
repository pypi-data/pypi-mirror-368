
from info2soft import config
from info2soft import https


class CommonTemplate (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 通用模板 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCommonTemplate(self, body):
        
        url = '{0}/common_template'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 通用模板 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeCommonTemplate(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/common_template/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 通用模板 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCommonTemplate(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/common_template/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 通用模板 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCommonTemplate(self, body):
        
        url = '{0}/common_template'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 通用模板 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCommonTemplate(self, body):
        
        url = '{0}/common_template'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

