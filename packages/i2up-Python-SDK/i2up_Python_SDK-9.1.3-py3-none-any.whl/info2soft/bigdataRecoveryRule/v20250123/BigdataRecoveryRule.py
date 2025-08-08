
from info2soft import config
from info2soft import https


class BigdataRecoveryRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 大数据恢复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataRecoveryRule(self, body):
        
        url = '{0}/vers/v3/bigdata/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据恢复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataRecoveryRule(self, body):
        
        url = '{0}/vers/v3/bigdata/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据恢复 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBigdataRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/bigdata/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 大数据恢复 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/bigdata/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 大数据恢复 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataRecoveryRuleStatus(self, body):
        
        url = '{0}/vers/v3/bigdata/recovery_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

