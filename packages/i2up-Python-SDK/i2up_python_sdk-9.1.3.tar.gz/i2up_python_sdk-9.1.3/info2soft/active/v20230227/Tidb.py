
from info2soft import config
from info2soft import https


class Tidb (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * tidb规则管理-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTidbRule(self, body):
        
        url = '{0}/tidb/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * tidb规则管理-修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyTidbRule(self, body):
        
        url = '{0}/tidb/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * tidb规则管理-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTidbRule(self, body):
        
        url = '{0}/tidb/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * tidb规则管理-获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTidbRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tidb/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * tidb规则管理-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeTidbRule(self, body):
        
        url = '{0}/tidb/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * tidb规则管理-规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTidbRules(self, body):
        
        url = '{0}/tidb/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * tidb规则管理-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTidbStatus(self, body):
        
        url = '{0}/tidb/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * tidb规则管理-日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTidbLog(self, body):
        
        url = '{0}/tidb/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

