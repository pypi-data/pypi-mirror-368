
from info2soft import config
from info2soft import https


class VpRecoveryRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpRecovery(self, body):
        
        url = '{0}/vp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRecoveryRule(self, body):
        
        url = '{0}/vp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpRecoveryRule(self, body):
        
        url = '{0}/vp/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateVpRecoveryRule(self, body):
        
        url = '{0}/vp/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRecoveryRuleStatus(self, body):
        
        url = '{0}/vp/recovery_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

