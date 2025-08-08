
from info2soft import config
from info2soft import https


class Sqlserver (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateRule(self, body):
        
        url = '{0}/sqlserver/rule/batch_add'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def duplicateSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAndStopAnalysisSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleStatus(self, body):
        
        url = '{0}/sqlserver/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量新建时重名检查
     * 
     * @return list
    '''
    def checkName(self, body):
        
        url = '{0}/sqlserver/rule/check_name'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmpStatus(self, body):
        
        url = '{0}/sqlserver/tb_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-日志（见通用同步规则信息日志接口）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):
        
        url = '{0}/sqlserver/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeListRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/sqlserver/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

