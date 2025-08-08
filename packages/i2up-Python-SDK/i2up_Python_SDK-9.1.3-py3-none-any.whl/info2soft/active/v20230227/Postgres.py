
from info2soft import config
from info2soft import https


class Postgres (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * postgres同步规则-列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPgsqlRule(self, body):
        
        url = '{0}/pgsql/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createPgsqlRule(self, body):
        
        url = '{0}/pgsql/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyPgsqlRule(self, body):
        
        url = '{0}/pgsql/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deletePgsqlRule(self, body):
        
        url = '{0}/pgsql/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumePgsqlRule(self, body):
        
        url = '{0}/pgsql/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * postgres规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPgsqlStatus(self, body):
        
        url = '{0}/pgsql/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * postgres 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPgsqlRuleLog(self, body):
        
        url = '{0}/pgsql/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * postgres获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describePgsqlRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/pgsql/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

