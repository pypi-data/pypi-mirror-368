
from info2soft import config
from info2soft import https


class Tape (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeRecovery(self, body):
        
        url = '{0}/tape_recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTapeRecovery(self, body):
        
        url = '{0}/tape_recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTapeRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape_recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTapeRecovery(self, body):
        
        url = '{0}/tape_recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeRecoveryStatus(self, body):
        
        url = '{0}/tape_recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

