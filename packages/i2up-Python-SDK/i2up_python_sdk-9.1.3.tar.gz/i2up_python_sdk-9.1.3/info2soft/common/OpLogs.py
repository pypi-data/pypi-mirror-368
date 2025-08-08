
from info2soft import config
from info2soft import https


class OpLogs (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 操作日志-获取操作日志列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOpLog(self, body):
        
        url = '{0}/op_log'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作日志-导入
     * 
     * @return list
    '''
    def importOpLog(self, body):

        url = '{0}/op_log/import'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * （未添加）操作日志-日志下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadOpLog(self, body):

        url = '{0}/op_log/download'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作日志-删除操作日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOpLog(self, body):

        url = '{0}/op_log'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 用户日志 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUserLog(self, body):

        url = '{0}/op_log/user_log'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

