# -*- coding: utf-8 -*-

from requests.auth import AuthBase

from info2soft.compat import urlparse
from info2soft import https
from info2soft import config
from info2soft.common.Cache import getToken, refreshToken


class Auth(object):
    """安全机制类

    Attributes:
        username: 账号
        pwd: 密码
        auth_type: 认证类型，token 或者 ak
        access_key: 密钥, auth_type 为 ak 的时候需要
        secret_key: 密钥, auth_type 为 ak 的时候需要
    """

    def __init__(self, username, pwd, auth_type='token', access_key='', secret_key=''):
        """初始化Auth类"""
        self.__checkKey(username, pwd)
        self._username = username
        self._pwd = pwd
        self._token = ''
        self._ssoToken = ''
        self.auth_type = auth_type
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = ''
        self.ssoToken = ''
        if auth_type == 'token':
            self.get_token()

    def get_username(self):
        return self._username

    def get_token(self):
        user = self._username
        pwd = self._pwd
        r = getToken(user, pwd)
        self._token = r[0]
        self._ssoToken = r[1]
        self.token = r[0]
        self.ssoToken = r[1]
        return self._token

    def refresh_token(self):
        r = refreshToken()
        self._token = r[0]
        self._ssoToken = r[1]
        self.token = r[0]
        self.ssoToken = r[1]
        return self

    '''
     * auth-注册账号(不开放)
     * 
     * @return list
    '''
    def regAccount(self, body):

        url = '{0}auth/register'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self)
        return res

    '''
     * 短信-1.时间戳
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimeStamp(self, body):

        url = '{0}/auth/t'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self)
        return res

    '''
     * 短信-2.生成短信、邮件关联信息
     * 
     * @return list
    '''
    def authGenerate(self, body):

        url = '{0}/auth/generate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self)
        return res

    '''
     * auth-获取手机、邮件验证码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVerificationCode(self, body):

        url = '{0}auth/verification_code'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self)
        return res

    '''
     * auth-检查用户是否需要验证码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkCaptcha(self, body):

        url = '{0}/auth/check_captcha'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self)
        return res

    '''
     * auth-获取token
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def tokendef(self, body):

        url = '{0}auth/token'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self)
        return res

    '''
     * auth-是否超时或账号失效
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def heartbeat(self, body):

        url = '{0}auth/heartbeat'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self)
        return res

    '''
     * 接口未实现
    '''
    def resetPwd(self, body):
        url = '{0}/auth/reset_password'.format(config.get_default('default_api_host'))
        r = https._post(url, body, self)
        return r

    def checkLoginStatus(self, body):
        url = '{0}/auth/token'.format(config.get_default('default_api_host'))
        data = {
            'access_token': self._ssoToken
        }
        r = https._get(url, data, self)
        return r

    def encryKey(self, body):
        url = '{0}/auth/encry_key'.format(config.get_default('default_api_host'))
        r = https._post(url, body, self)
        return r

    def token_of_request(self, url, body=None, content_type=None):
        parsed_url = urlparse(url)
        query = parsed_url.query
        path = parsed_url.path
        data = path
        if query != '':
            data = ''.join([data, '?', query])
        data = ''.join([data, "\n"])

        if body:
            mimes = [
                'application/x-www-form-urlencoded'
            ]
            if content_type in mimes:
                data += body

        return '{0}'.format(self._token)

    @staticmethod
    def __checkKey(username, pwd):
        if not (username and pwd):
            raise ValueError('invalid key')

    def verify_callback(self, origin_authorization, url, body, content_type='application/x-www-form-urlencoded'):
        """回调验证

        Args:
            origin_authorization: 回调时请求Header中的Authorization字段
            url:                  回调请求的url
            body:                 回调请求的body
            content_type:         回调请求body的Content-Type

        Returns:
            返回true表示验证成功，返回false表示验证失败
        """
        token = self.token_of_request(url, body, content_type)
        authorization = 'QBox {0}'.format(token)
        return origin_authorization == authorization


class RequestsAuth(AuthBase):
    def __init__(self, auth):
        self.auth = auth

    def __call__(self, r):
        if r.body is not None and r.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            token = self.auth.token_of_request(r.url, r.body, 'application/x-www-form-urlencoded')
        else:
            token = self.auth.token_of_request(r.url)
        r.headers['Authorization'] = '{0}'.format(token)
        return r