
from info2soft import config
from info2soft import https


class RetentionPolicy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 全局保留期限设置 - 获取列表
     * 
     * @return list
    '''
    def listRetentionPolicy(self, body):
        
        url = '{0}/vers/v3/retention_policy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 全局保留期限设置 - 修改保留期限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRetentionPoliciy(self, body):
        
        url = '{0}/vers/v3/retention_policy'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

