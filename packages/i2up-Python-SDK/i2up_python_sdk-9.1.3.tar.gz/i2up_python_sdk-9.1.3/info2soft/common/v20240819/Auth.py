
from info2soft import config
from info2soft import https


class Auth (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 短信-1.时间戳
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimeStamp(self, body):
        
        url = '{0}/auth/t'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 短信-2.生成短信、邮件、图片验证码关联信息
     * 
     * @return list
    '''
    def authGenerate(self, body):
        
        url = '{0}/auth/generate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * auth-获取手机、邮件、图片验证码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVerificationCode(self, body):
        
        url = '{0}/auth/verification_code'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * auth-检查用户是否需要验证码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkCaptcha(self, body):
        
        url = '{0}/auth/check_captcha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * auth-获取token
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def token(self, body):
        
        url = '{0}/auth/token'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * auth-重置密码
     * 
     * @return list
    '''
    def resetPwd(self, body):
        
        url = '{0}/auth/reset_password'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * auth-check用户登录状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkLoginStatus(self, body):
        
        url = '{0}/auth/token'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * auth-注册账号(不开放)
     * 
     * @return list
    '''
    def regAccount(self, body):
        
        url = '{0}/auth/register'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * auth-是否超时或账号失效
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def heartbeat(self, body):
        
        url = '{0}/auth/heartbeat'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

