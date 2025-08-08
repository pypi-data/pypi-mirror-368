
from info2soft import config
from info2soft import https


class Oceanbase (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则列表
     * 
     * @return list
    '''
    def listOceanRule(self, ):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 批量新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchOceanRule(self, body):
        
        url = '{0}/ocean/rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改规则
     * 
     * @return list
    '''
    def modifyOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, None, self.auth)
        return res

    '''
     * 单条规则
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
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOceanRule(self, body):
        
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeOceanRule(self, body):
        
        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOceanRuleLog(self, body):
        
        url = '{0}/ocean/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Oceanbase表修复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createOceanTableFix(self, body):
        
        url = '{0}/ocean/rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

