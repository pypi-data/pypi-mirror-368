
from info2soft import config
from info2soft import https


class RestrpcServer (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取规则和任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRestRpcTasks(self, body):
        
        url = '{0}/client/rest_rpc/task_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 底层推送日志接口，日志、状态等
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcLog(self, body):
        
        url = '{0}/client/rest_rpc/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 上报结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcresult(self, body):
        
        url = '{0}/client/rest_rpc/result'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取控制机IP或节点代理开关
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRestRpcCcip(self, body):
        
        url = '{0}/client/rest_rpc/cc_ip'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Ha动态节点切换后上报接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcHa(self, body):
        
        url = '{0}/client/rest_rpc/ha'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 服务器池更新底层传上来的中心节点IP
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcCluster(self, body):
        
        url = '{0}/client/rest_rpc/cluster'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 云主机 - 创建结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyEcs(self, body):

        url = '{0}/client/rest_rpc/cloud_ecs'.format(config.get_default('default_api_host'))
        print(url)
        res = https._put(url, body, self.auth)
        return res

    '''
     * 快速注册节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerNodeFromNode(self, body):

        url = '{0}/client/rest_rpc/node'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res



