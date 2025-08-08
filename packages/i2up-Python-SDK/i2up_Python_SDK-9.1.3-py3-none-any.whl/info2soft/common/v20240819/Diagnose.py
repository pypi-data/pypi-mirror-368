
from info2soft import config
from info2soft import https


class Diagnose (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 诊断 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 诊断 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 诊断 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取虚机规则列表
     * 
     * @return list
    '''
    def listVpRules(self, body):
        
        url = '{0}/diagnose/list_vp_rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

