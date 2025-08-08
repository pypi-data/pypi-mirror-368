
from info2soft import config
from info2soft import https
from info2soft.common.Rsa import Rsa


class User (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新增用户
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def createUser(self, body):
        url = '{0}/user'.format(config.get_default('default_api_host'))
        rsa = Rsa()
        password = rsa.rsaEncrypt(body['password'])
        body.update({'password': password})
        res = https._post(url, body, self.auth)
        return res

    '''
     * 用户列表(admin)
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取用户
     * 
     * @return array
     '''
    def describeUser(self, body):
        
        url = '{0}/user/{1}'.format(config.get_default('default_api_host'), body['user_uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除账户
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def deleteUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 修改用户信息
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def modifyUser(self, body):
        url = '{0}/user/{1}'.format(config.get_default('default_api_host'), body['ids'])
        rsa = Rsa()
        password = rsa.rsaEncrypt(body['password'])
        body.update({'password': password})
        res = https._put(url, body, self.auth)
        return res

    '''
     * 修改密码
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def modifyUserPwd(self, body):
        
        url = '{0}/user/password'.format(config.get_default('default_api_host'))
        rsa = Rsa()
        password = rsa.rsaEncrypt(body['password'])
        oldPwd = rsa.rsaEncrypt(body['old_password'])
        body.update({'password': password, 'old_password': oldPwd})
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取用户Profile
     * 
     * @return array
     '''
    def listProfile(self, ):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 修改Profile
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def modifyProfile(self, body):
        
        url = '{0}/user/profile'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 退出登录
     * 
     * @return array
     '''
    def logout(self, ):
        
        url = '{0}/user/logout'.format(config.get_default('default_api_host'))

        res = https._post(url, None, self.auth)
        return res

    '''
     * ---- 密钥管理 -----
     * 
     * @return list
     '''

    '''
     * AccessKey列表
     * 
     * @return list
     '''

    def listAk(self, ):
        url = '{0}/ak'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res

    '''
     * AccessKey新建
     * 
     * @return list
     '''

    def createAk(self, ):
        url = '{0}/ak'.format(config.get_default('default_api_host'))

        res = https._post(url, None, self.auth)
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

    '''
     * ----  角色管理 -----
     * 
     * @return list
     '''

    '''
     *  角色列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listRole(self, body):
        url = '{0}/role'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

