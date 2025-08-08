
from info2soft import config
from info2soft import https


class DbInstance (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 发现实例
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def discoveryDbInstances(self, body):
        
        url = '{0}/vers/v3/db_instance/discovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 认证实例
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyDbInstances(self, body):
        
        url = '{0}/db_instance/verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDbInstance(self, body):
        
        url = '{0}/vers/v3/db_instance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbInstances(self, body):
        
        url = '{0}/vers/v3/db_instance'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDbInstance(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/db_instance/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDbInstance(self, body):
        
        url = '{0}/db_instance'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDbInstances(self, body):
        
        url = '{0}/db_instance'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取数据库列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbs(self, body):
        
        url = '{0}/db_instance/list_db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取数据库表list
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTables(self, body):
        
        url = '{0}/db_instance/list_tables'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取数据库表空间list
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTableSpaces(self, body):
        
        url = '{0}/db_instance/list_table_spaces'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

