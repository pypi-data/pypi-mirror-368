
from info2soft import config
from info2soft import https


class Log (object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 告警日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLogWarning(self, body):

        url = '{0}/active/log_warning'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 告警日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):

        url = '{0}/active/log_warning'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

