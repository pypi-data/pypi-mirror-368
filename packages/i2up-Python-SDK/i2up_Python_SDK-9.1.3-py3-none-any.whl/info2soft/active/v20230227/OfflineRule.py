
from info2soft import config
from info2soft import https


class OfflineRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 离线同步 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOfflineRule(self, body):
        
        url = '{0}/offline_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 离线同步 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createActiveOfflineRule(self, body):
        
        url = '{0}/offline_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 离线同步 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyActiveOfflineRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/offline_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 离线同步 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOfflineRuleStatus(self, body):
        
        url = '{0}/offline_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 离线同步 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOfflineRule(self, body):
        
        url = '{0}/offline_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 离线同步 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateOfflineRule(self, body):
        
        url = '{0}/offline_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 离线同步 - 字符集
     * 
     * @return list
    '''
    def getOfflineRuleCharset(self, body):
        
        url = '{0}/offline_rule/charset'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

