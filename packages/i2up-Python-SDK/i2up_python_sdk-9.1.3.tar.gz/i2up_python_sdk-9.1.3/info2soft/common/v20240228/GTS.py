
from info2soft import config
from info2soft import https


class GTS (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 解析许可授权
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeLic(self, body):
        
        url = '{0}/lic/describe'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 关闭服务
     * 
     * @return list
    '''
    def closeService(self, body, uuid):
        
        url = '{0}/gts/service/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 服务列表list
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listService(self, body, uuid):
        
        url = '{0}/gts/service/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 添加服务器
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createServer(self, body):
        
        url = '{0}/gts/hello'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 租户授权详情
     * 
     * @return list
    '''
    def describeQuota(self, body):
        
        url = '{0}/gts/quota'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 控制台概要
     * 
     * @return list
    '''
    def describeSummary(self, body):
        
        url = '{0}/gts/summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

