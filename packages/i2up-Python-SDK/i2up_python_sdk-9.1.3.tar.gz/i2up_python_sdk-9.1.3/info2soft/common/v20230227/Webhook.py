
from info2soft import config
from info2soft import https


class Webhook (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * webhook渠道 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createWebhook(self, body):
        
        url = '{0}/webhook'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Webhook渠道 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyWebhook(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/webhook/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Webhook渠道 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listWebhook(self, body):
        
        url = '{0}/webhook'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Webhook渠道 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeWebhook(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/webhook/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Webhook渠道 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteWebhook(self, body):
        
        url = '{0}/webhook'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 内容模板 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createWebhookContentTemplate(self, body):
        
        url = '{0}/webhook/content_template'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 内容模板 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyWebhookContentTemplate(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/webhook/content_template/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 内容模板 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listWebhookContentTemplate(self, body):
        
        url = '{0}/webhook/content_template'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 内容模板 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def delteWebhookContentTemplate(self, body):
        
        url = '{0}/webhook/content_template'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

