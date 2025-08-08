
from info2soft import config
from info2soft import https


class Infomix (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createInformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteInformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeInformixRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'
        
        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopInformixRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartInformixRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisInformixRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/informix/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 单条规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeInformixRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/informix/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则列表
     * 
     * @return list
    '''
    def listinformixRule(self, body):
        
        url = '{0}/informix/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

