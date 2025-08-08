
from info2soft import config
from info2soft import https


class Mysql (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMysqlRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamRules(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyMysqlRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchMysqlRule(self, body):
        
        url = '{0}/stream/rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchModifyMysqlRule(self, body):
        
        url = '{0}/stream/rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMysqlRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeMysqlRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startParsingMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopParsingMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetParsingMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startLoadMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopLoadMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetLoadMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def duplicateMysqlRule(self, body):
        
        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 状态（详细返回参考Oracle同步规则状态接口）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamStatus(self, body):
        
        url = '{0}/stream/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-表修复-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStreamTableFix(self, body):
        
        url = '{0}/stream/rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取LSN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getStreamRuleLsn(self, body):
        
        url = '{0}/stream/rule/lsn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

