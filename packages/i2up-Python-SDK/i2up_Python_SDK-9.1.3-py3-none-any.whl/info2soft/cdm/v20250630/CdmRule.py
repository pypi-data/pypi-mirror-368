
from info2soft import config
from info2soft import https


class CdmRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 接管/演练 --- 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def takeOverDrillList(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTakeOverDrill(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 接管/演练 --- 获取虚机状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmStatus(self, body):
        
        url = '{0}/cdm_rule/vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def openConsoleTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

