
from info2soft import config
from info2soft import https


class SensCheck (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 敏感发现 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSensCheck(self, body):
        
        url = '{0}/vers/v3/mask/sens_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySensCheck(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_check/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSensCheck(self, body):
        
        url = '{0}/vers/v3/mask/sens_check'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startMaskRule(self, body):
        
        url = '{0}/vers/v3/mask/sens_check/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopMaskRule(self, body):
        
        url = '{0}/vers/v3/mask/sens_check/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheck(self, body):
        
        url = '{0}/vers/v3/mask/sens_check'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptSensCheck(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_check/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 敏感发现 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckStatus(self, body):
        
        url = '{0}/vers/v3/mask/sens_check/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 结果
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckResult(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_check/result/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 敏感发现 - 忽略结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckIgnoreCol(self, body):
        
        url = '{0}/vers/v3/mask/sens_check/ignore_col'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

