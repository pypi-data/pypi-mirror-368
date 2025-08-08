
from info2soft import config
from info2soft import https


class Menu (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取菜单列表
     * 
     * @return list
    '''
    def listMenu(self, body):
        
        url = '{0}/menu'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

