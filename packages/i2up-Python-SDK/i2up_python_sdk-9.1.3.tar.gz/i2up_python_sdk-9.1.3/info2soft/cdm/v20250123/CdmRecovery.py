
from info2soft import config
from info2soft import https


class CdmRecovery (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 整机恢复 --- 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebootCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRecoveryStatus(self, body):
        
        url = '{0}/cdm_recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

