
from info2soft import config
from info2soft import https


class Notifications (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 消息 列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listNotifications(self, body):
        
        url = '{0}/notifications'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 消息 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def describeNotifications(self, body):
        if body is None or 'uuid' not in body:
            exit()
        url = '{0}/notifications/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 消息 数量
     * 
     * @return array
     '''
    def describeNotificationsCount(self):
        
        url = '{0}/notifications/count'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 消息 操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def deleteNotifications(self, body):
        
        url = '{0}/notifications/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    def readNotifications(self, body):

        url = '{0}/notifications/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置 获取
     * 
     * @return array
     '''
    def describeNotificationsConfig(self, ):
        
        url = '{0}/notifications/config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 配置 更新
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def updateNotificationsConfig(self, body):
        
        url = '{0}/notifications/config'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 邮件测试
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def testNotificationsEmail(self, body):
        
        url = '{0}/notifications/email_test'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 重置通知次数
     * 
     * @return array
     '''
    def resetNotificationsTimes(self, ):
        
        url = '{0}/notifications/reset_notify_times'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 消息 添加
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def addNotifications(self, body):
        url = '{0}/notifications'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 短信测试
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def testNotificationsSms(self, body):
        url = '{0}/notifications/sms_test'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res
