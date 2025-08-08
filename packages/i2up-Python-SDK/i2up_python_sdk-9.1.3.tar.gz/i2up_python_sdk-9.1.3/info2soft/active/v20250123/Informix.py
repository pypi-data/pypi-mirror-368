
from info2soft import config
from info2soft import https


class Informix (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createInformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteInformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeInformixRule(self, body):
        
        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopInformixRule(self, body):
        
        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartInformixRule(self, body):
        
        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisInformixRule(self, body):
        
        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def describeInformixRule(self, body, id):
        if id is None:
            exit()
        url = '{0}/informix/rule/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 列表
     * 
     * @return list
    '''
    def listinformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

