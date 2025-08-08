
from info2soft import config
from info2soft import https


class Permission (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取权限列表
     * 
     * @return list
    '''
    def listPermission(self, body):
        
        url = '{0}/permission'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 权限 - 类别
     * 
     * @return list
    '''
    def listCategory(self, body):
        
        url = '{0}/permission/category'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 权限 - 类别权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCatPerms(self, body):
        
        url = '{0}/permission/cat_perms'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 权限 - 类别权限（9版本双门户）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCatPerms9(self, body):
        
        url = '{0}/permission/cat_perms9'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

