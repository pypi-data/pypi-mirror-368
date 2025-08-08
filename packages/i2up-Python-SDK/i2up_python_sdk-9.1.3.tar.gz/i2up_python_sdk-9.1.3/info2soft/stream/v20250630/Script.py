
from info2soft import config
from info2soft import https


class Script (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 自定义脚本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createScript(self, body):
        
        url = '{0}/vers/v3/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自定义脚本 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyScript(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/script/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 自定义脚本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteScript(self, body):
        
        url = '{0}/vers/v3/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 自定义脚本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listScript(self, body):
        
        url = '{0}/vers/v3/mask/script'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自定义脚本 - 下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadScript(self, body):
        
        url = '{0}/vers/v3/mask/script/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自定义脚本 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptScript(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/script/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

