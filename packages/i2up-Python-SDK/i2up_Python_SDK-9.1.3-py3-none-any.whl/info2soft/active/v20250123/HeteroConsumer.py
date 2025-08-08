
from info2soft import config
from info2soft import https


class HeteroConsumer (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 异构-消费-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createConsumerRule(self, body):
        
        url = '{0}/vers/v3/consumer_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费-修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyConsumerRule(self, body):
        
        url = '{0}/vers/v3/consumer_rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 异构-消费-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteConsumerRules(self, body):
        
        url = '{0}/vers/v3/consumer_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 异构-消费-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listConsumerStatus(self, body):
        
        url = '{0}/vers/v3/consumer_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-消费-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopConsumerRule(self, body):
        
        url = '{0}/vers/v3/consumer_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeConsumerRule(self, body):
        
        url = '{0}/vers/v3/consumer_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费-获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listConsumerRules(self, body):
        
        url = '{0}/vers/v3/consumer_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-消费-获取单条规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeConsumerRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/consumer_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

