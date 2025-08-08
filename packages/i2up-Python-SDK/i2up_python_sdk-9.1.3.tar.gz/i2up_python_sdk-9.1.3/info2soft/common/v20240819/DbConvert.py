
from info2soft import config
from info2soft import https


class DbConvert (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 上传备份数据
     * 
     * @return list
    '''
    def dbConvertImport(self, body):
        
        url = '{0}/db_convert/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取convert列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dbConvertListConverts(self, body):
        
        url = '{0}/db_convert/convert_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 执行迁移
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dbConvertMigrate(self, body):
        
        url = '{0}/db_convert/migrate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

