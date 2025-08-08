from info2soft import config
from info2soft import https


class UpMonitor(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     *  认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def authUpMonitor(self, body):
        url = '{0}/up_monitor/auth'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取子平台token
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeUpMonitorToken(self, body):
        url = '{0}/up_monitor/token'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createUpMonitor(self, body):
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 子平台 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUpMonitor(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/up_monitor/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._put(url, body, self.auth)
        return res

    '''
     * 子平台 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeUpMonitor(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/up_monitor/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listUpMonitor(self, body):
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def refreshUpMonitor(self, body):
        if body is None:
            body = {
                'operate': 'refresh'
            }
        else:
            body['operate'] = 'refresh'
        url = '{0}/up_monitor/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listUpMonitorStatus(self, body):
        url = '{0}/up_monitor/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteUpMonitor(self, body):
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

