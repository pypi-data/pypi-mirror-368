
from info2soft import config
from info2soft import https


class Credential (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCredential(self, body):
        
        url = '{0}/credential'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCredential(self, body):
        
        url = '{0}/credential'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeCredential(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/credential/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCredential(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/credential/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCredential(self, body):
        
        url = '{0}/credential'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 批量导入下载模板
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadTemplate(self, body):
        
        url = '{0}/dl'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 批量导入
     * 
     * @return list
    '''
    def batchImportCredential(self, body):
        
        url = '{0}credential/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

