
from info2soft import config
from info2soft import https


class Notifications (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 消息接收管理-更新更多配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateNotifyConf(self, body):
        
        url = '{0}/sys/settings/notify_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 消息接收管理-获取配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNotifyConf(self, body):
        
        url = '{0}/sys/settings/notify_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 消息 添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addNotifications(self, body):
        
        url = '{0}/notifications'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 消息 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNotifications(self, body):
        
        url = '{0}/notifications'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 消息 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeNotifications(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/notifications/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 消息 数量
     * 
     * @return list
    '''
    def describeNotificationsCount(self, body):
        
        url = '{0}/notifications/count'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 消息 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def readNotifications(self, body):
        
        url = '{0}/notifications/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 消息 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def playNotifications(self, body):
        
        url = '{0}/notifications/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 消息 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNotifications(self, body):
        
        url = '{0}/notifications'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 配置 获取
     * 
     * @return list
    '''
    def describeNotificationsConfig(self, body):
        
        url = '{0}/notifications/config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 配置 更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateNotificationsConfig(self, body):
        
        url = '{0}/notifications/config'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 短信测试
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def testNotificationsSms(self, body):
        
        url = '{0}/notifications/sms_test'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 邮件测试
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def testNotificationsEmail(self, body):
        
        url = '{0}/notifications/email_test'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 重置通知次数
     * 
     * @return list
    '''
    def resetNotificationsTimes(self, body):
        
        url = '{0}/notifications/reset_notify_times'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 邮件模板 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEmailTemplate(self, body):
        
        url = '{0}/notifications/template'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 邮件模板 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyEmailTemplate(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/notifications/template/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

