
from info2soft import config
from info2soft import https


class TapeCopy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeCopy(self, body):
        
        url = '{0}/tape_copy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTapeCopy(self, body):
        
        url = '{0}/tape_copy'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTapeCopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape_copy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeCopyStatus(self, body):
        
        url = '{0}/tape_copy/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTapeCopy(self, body):
        
        url = '{0}/tape_copy'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

