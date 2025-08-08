
from info2soft import config
from info2soft import https


class Redis (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRedisRule(self, body):
        
        url = '{0}/redis/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRedisRule(self, body, uuid):
        
        url = '{0}/redis/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRedisRule(self, body):
        
        url = '{0}/redis/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 启/停/重新同步/继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeRedisRule(self, body):
        
        url = '{0}/redis/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRedisStatus(self, body):
        
        url = '{0}/redis/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRedisRuleLog(self, body):
        
        url = '{0}/redis/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRedisRule(self, body):
        
        url = '{0}/redis/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个规则
     * 
     * @return list
    '''
    def describeRedisRule(self, body, uuid):
        
        url = '{0}/redis/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

