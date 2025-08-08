
from info2soft import config
from info2soft import https


class Drill (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 自动演练规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdmDrill(self, body):
        
        url = '{0}/cdm_drill'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdmDrill(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_drill/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 自动演练规则 - 获取组
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdmDrillGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_drill/{1}/group'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 自动演练规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCdmDrill(self, body):
        
        url = '{0}/cdm_drill'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCdmDrill(self, body):
        
        url = '{0}/cdm_drill/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startCdmDrill(self, body):
        
        url = '{0}/cdm_drill/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def setStatusCdmDrill(self, body):
        
        url = '{0}/cdm_drill/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmDrillStatus(self, body):
        
        url = '{0}/cdm_drill/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 获取虚机状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def queryGroupVmStatus(self, body):
        
        url = '{0}/cdm_drill/vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

