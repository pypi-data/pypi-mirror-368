from info2soft import config
from info2soft import https


class Logs(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * i2node日志-规则/任务日志（uuid）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTaskLog(self, body):
        url = '{0}/logs'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * i2node日志-HA日志（uuid_m_uuid）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listHALog(self, body):
        url = '{0}/logs/ha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * i2node日志-节点日志（m_uuid）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listNodeLog(self, body):
        url = '{0}/logs/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * npsvr日志-任务日志
     * 
     * @return list
    '''

    def listNpsvrLog(self, body):
        url = '{0}/logs/npsvr'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * traffic日志-logs.traffic
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTrafficLog(self, body):
        url = '{0}/logs/traffic'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * logserver-上传统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def collectStatistics(self, body):

        url = '{0}/collect_statistics'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

