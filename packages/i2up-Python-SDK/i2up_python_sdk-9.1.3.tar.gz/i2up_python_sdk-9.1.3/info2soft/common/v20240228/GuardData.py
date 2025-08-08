
from info2soft import config
from info2soft import https


class GuardData (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 节点管理 - 检查防篡改功能是否可用
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeGuardDataEnabled(self, body):
        
        url = '{0}/guard_data/node_guard_data_enabled'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取节点策略列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGuardData(self, body):
        
        url = '{0}/guard_data'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建策略
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createGuardData(self, body):
        
        url = '{0}/guard_data'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改策略
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyGuardData(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/guard_data/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除策略
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteGuardData(self, body):
        
        url = '{0}/guard_data'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取防篡改节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/guard_data/node_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取节点数据保护日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGuardDataLogs(self, body):
        
        url = '{0}/guard_data/list_guard_data_logs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 威胁感知
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def threatPerception(self, body):
        
        url = '{0}/guard_data/threat_perception'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

