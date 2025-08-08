
from info2soft import config
from info2soft import https


class Notifications (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 消息通知（告警）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNotify(self, body):
        
        url = '{0}/api/notifications/active_notify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

