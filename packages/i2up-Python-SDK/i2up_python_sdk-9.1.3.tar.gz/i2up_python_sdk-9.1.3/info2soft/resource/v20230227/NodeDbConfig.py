
from info2soft import config
from info2soft import https


class NodeDbConfig (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 数据库配置信息-发现实例
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeGetDatabaseInstances(self, body):
        
        url = '{0}/node/db_instances'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库信息配置 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNodeDbConfig(self, body):
        
        url = '{0}/node/db_config'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库信息配置 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeDbConfig(self, body):
        
        url = '{0}/node/db_config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

