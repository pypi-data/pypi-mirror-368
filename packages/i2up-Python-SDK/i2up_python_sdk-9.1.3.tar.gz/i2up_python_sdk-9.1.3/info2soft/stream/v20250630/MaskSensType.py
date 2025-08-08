
from info2soft import config
from info2soft import https


class MaskSensType (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 敏感类型 - 修改
     * 
     * @body['id'] String  必填 id
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySensType(self, body, id):
        if id is None:
            exit()
        url = '{0}/vers/v3/mask/sens_type/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 敏感类型 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTypes(self, body):
        
        url = '{0}/vers/v3/mask/sens_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 敏感类型 - 单个
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def descriptSensType(self, body, id):
        if id is None:
            exit()
        url = '{0}/vers/v3/mask/sens_type/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

