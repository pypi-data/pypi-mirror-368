
from info2soft import config
from info2soft import https


class FindPassword (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 判断账号是否存在
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def isAccountExists(self, body):
        
        url = '{0}/find_password/account'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 发送验证码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def sendVerificationCode(self, body):
        
        url = '{0}/find_password/account_verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 验证码校验
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyVerficationCode(self, body):
        
        url = '{0}/find_password/verification_code_verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 密码重置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetPassword(self, body):
        
        url = '{0}/find_password/reset_password'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

