
from info2soft import config
from info2soft import https


class RocketMq (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * RocketMQ同步 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRocketMqRule(self, body):
        
        url = '{0}/rocketmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRocketMqRule(self, body):
        
        url = '{0}/rocketmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRocketMqRules(self, body):
        
        url = '{0}/rocketmq/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRocketMqStatus(self, body):
        
        url = '{0}/rocketmq/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRocketMqRule(self, body):
        
        url = '{0}/rocketmq/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeRocketMqRule(self, body):
        
        url = '{0}/rocketmq/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRocketMqRules(self, body):
        
        url = '{0}/rocketmq/viewtype'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * RocketMQ同步 - 单条
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRocketMqRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rocketmq/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

