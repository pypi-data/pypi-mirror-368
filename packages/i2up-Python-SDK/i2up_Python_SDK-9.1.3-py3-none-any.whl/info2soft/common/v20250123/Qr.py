
from info2soft import config
from info2soft import https


class Qr (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 二维码-1.时间戳
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimeStamp(self, body):
        
        url = '{0}/qr/t'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 二维码-2.获取二维码内容
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def obtainQrContent(self, body):
        
        url = '{0}/qr/generate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二维码-3.生成二维码图片
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createQrPic(self, body):
        
        url = '{0}/qr'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 二维码-4.确认/取消登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def confirmLogin(self, body):
        
        url = '{0}/qr/event'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二维码-4.确认/取消登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cancelLogin(self, body):
        
        url = '{0}/qr/event'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二维码-4.确认/取消登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkQrValidity(self, body):
        
        url = '{0}/qr/event'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二维码-5.检查二维码状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkQrStatus(self, body):
        
        url = '{0}/qr/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

