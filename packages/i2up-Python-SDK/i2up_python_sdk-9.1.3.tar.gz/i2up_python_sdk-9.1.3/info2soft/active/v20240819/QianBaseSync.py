
from info2soft import config
from info2soft import https


class QianBaseSync (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseStatus(self, body):
        
        url = '{0}/qianbase/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseRuleLog(self, body):
        
        url = '{0}/qianbase/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQianbaseRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/qianbase/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

