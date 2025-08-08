
from info2soft import config
from info2soft import https


class UserSettings (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 用户Profile(all user)-获取用户Profile
     * 
     * @return list
    '''
    def listProfile(self, body):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 用户Profile(all user)-修改密码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUserPwd(self, body):
        
        url = '{0}/user/password'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户修改个人资料
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyProfile(self, body):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户修改消息推送地址
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUserNotifyAddr(self, body):
        
        url = '{0}/user/notify_addr'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户Profile(all user)-退出登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def logout(self, body):
        
        url = '{0}/user/logout'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2FA - 当前信息
     * 
     * @return list
    '''
    def describeTwoFactor(self, body):
        
        url = '{0}/2fa'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 2FA - 获取绑定信息
     * 
     * @return list
    '''
    def describeOtp(self, body):
        
        url = '{0}/2fa/otp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 2FA - 生成新恢复码
     * 
     * @return list
    '''
    def renewRecoveryCode(self, body):
        
        url = '{0}/2fa/recovery_code'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 2FA - 配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def configTwoFactor(self, body):
        
        url = '{0}/2fa'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * AccessKey列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * AccessKey新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * AccessKey更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * AccessKey删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAk(self, body):
        
        url = '{0}/ak'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

