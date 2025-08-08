
from info2soft import config
from info2soft import https


class Hetero (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 异构-消费-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createConsumerRule(self, body):
        
        url = '{0}/hetero/consumer/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费-修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyConsumerRule(self, body):
        
        url = '{0}/hetero/consumer/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 异构-消费-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteConsumerRules(self, body):
        
        url = '{0}/hetero/consumer/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 异构-消费-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listConsumerStatus(self, body):
        
        url = '{0}/hetero/consumer/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-消费-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopConsumerRule(self, body):
        
        url = '{0}/hetero/consumer/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费-获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listConsumerRules(self, body):
        
        url = '{0}/hetero/consumer/viewtype'.format(config.get_default('default_api_host'))
        
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
        url = '{0}/hetero/consumer/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHeteroGraph(self, body):
        
        url = '{0}/hetero/graph'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addHeteroGraph(self, body):
        
        url = '{0}/hetero/graph/add'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHeteroGraph(self, body):
        
        url = '{0}/hetero/graph/list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-运行拓扑
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def runHeteroGraph(self, body):
        
        url = '{0}/hetero/graph/run'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-停止拓扑
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopHeteroGraph(self, body):
        
        url = '{0}/hetero/graph/stop'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGraphStatus(self, body):
        
        url = '{0}/hetero/graph/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-删除拓扑
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHeteroGraph(self, body):
        
        url = '{0}/hetero/graph'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 异构-拓扑-拓扑详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptGraphDetail(self, body):
        
        url = '{0}/hetero/graph/detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-拓扑图-获取拓扑图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGraph(self, body):
        
        url = '{0}/hetero/graph/graph'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-新建(暂弃用)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHeteroRule(self, body):
        
        url = '{0}/hetero/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-消费 （暂弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def consumer(self, body):
        
        url = '{0}/hetero/consumer'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-删除（暂弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHeteroRule(self, body):
        
        url = '{0}/hetero'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 异构-查看消费者（暂弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createConsumer(self, body):
        
        url = '{0}/hetero/view_consumer'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 异构-查看topic（暂弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHeteroTopic(self, body):
        
        url = '{0}/hetero/topic'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 异构-获取列表（暂弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHeteroRule(self, body):
        
        url = '{0}/hetero/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

