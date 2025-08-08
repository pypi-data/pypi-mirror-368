
from info2soft import config
from info2soft import https


class Rabbitmq (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 列表
     * 
     * @return list
    '''
    def listRabbitmqRule(self, body):
        
        url = '{0}/rabbitmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRabbitMqRule(self, body):
        
        url = '{0}/rabbitmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @return list
    '''
    def modifyRabbitmqRule(self, body):
        
        url = '{0}/rabbitmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRabbitmqRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rabbitmq/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRabbitmqRule(self, body):
        
        url = '{0}/rabbitmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeRabbitmqRule(self, body):
        
        url = '{0}/rabbitmq/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRabbitmqRule(self, body):
        
        url = '{0}/rabbitmq/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesStatus(self, body):
        
        url = '{0}/rabbitmq/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

