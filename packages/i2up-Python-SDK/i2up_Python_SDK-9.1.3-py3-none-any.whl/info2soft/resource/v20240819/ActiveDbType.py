
from info2soft import config
from info2soft import https


class ActiveDbType (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 数据库支持类型 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listActiveDbType(self, body):
        
        url = '{0}/vers/v3/active/db_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库支持类型 - 支持的映射类型
     * 
     * @return list
    '''
    def listActiveDbTypeAvailMappingType(self, body):
        
        url = '{0}/vers/v3/active/db_type/mapping_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 数据库支持类型 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createActiveDbType(self, body):
        
        url = '{0}/vers/v3/active/db_type'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库支持类型 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyActiveDbType(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/active/db_type/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 数据库支持类型 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteActiveDbType(self, body):
        
        url = '{0}/vers/v3/active/db_type'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取特定菜单可用源端类型 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAvailActiveDbSourceType(self, body):
        
        url = '{0}/vers/v3/active/db_type/avail_src_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库备端支持类型 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAvailActiveDbType(self, body):
        
        url = '{0}/vers/v3/active/db_type/avail_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库备端支持类型 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAvailActiveDbType(self, body):
        
        url = '{0}/vers/v3/active/db_type/type_mapping'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

