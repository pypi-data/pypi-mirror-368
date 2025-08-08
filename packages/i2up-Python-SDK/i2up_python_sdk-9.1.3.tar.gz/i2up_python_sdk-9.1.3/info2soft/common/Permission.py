
from info2soft import config
from info2soft import https


class Permission (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * categories
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listCategory(self, body):
        
        url = '{0}/permission/category'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  类别权限
     * 
     * @return list
     '''

    def listCatPerms(self, body):
        url = '{0}/permission/cat_perms'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res
