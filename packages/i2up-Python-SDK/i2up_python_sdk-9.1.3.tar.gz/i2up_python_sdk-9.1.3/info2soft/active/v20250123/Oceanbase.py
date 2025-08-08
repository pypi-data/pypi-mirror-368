
from info2soft import config
from info2soft import https


class Oceanbase (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 列表
     * 
     * @return list
    '''
    def listOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchOceanRule(self, body):
        
        url = '{0}/ocean/rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @return list
    '''
    def modifyOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeOceanRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ocean/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetAnalysisOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def duplicateOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesStatus(self, body):
        
        url = '{0}/ocean/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createOceanTableFix(self, body):
        
        url = '{0}/ocean/rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

