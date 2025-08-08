
from info2soft import config
from info2soft import https


class SensMap (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 敏感集合 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_db_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 敏感集合 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 敏感集合 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 敏感集合 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 敏感集合 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 类型列表 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDbMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 类型列表 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 类型列表 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDbMap(self, body):
        
        url = '{0}/vers/v3/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 类型列表 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def modifyDbMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/mask/sens_db_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

