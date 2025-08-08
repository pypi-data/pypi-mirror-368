
from info2soft import config
from info2soft import https


class MysqlRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备端接管-获取网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBkTakeoveNetworkCard(self, body):
        
        url = '{0}/stream/bk_takeover/bk_network_card'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备端接管-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管-查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBkTakeover(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/bk_takeover/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备机接管-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备机接管-接管结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBkTakeoverResult(self, body):
        
        url = '{0}/stream/bk_takeover/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备机接管-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管-获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBkTakeoverStatus(self, body):
        
        url = '{0}/stream/bk_takeover/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管列表
     * 
     * @return list
    '''
    def listBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

