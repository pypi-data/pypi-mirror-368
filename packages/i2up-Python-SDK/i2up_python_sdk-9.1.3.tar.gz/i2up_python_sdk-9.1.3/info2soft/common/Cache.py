from info2soft.common.Rsa import Rsa
from info2soft import https
from info2soft import config
import linecache
import os


def getToken(username, pwd):
    token = ''
    ssoToken = ''
    # path = os.path.split(os.path.realpath(__file__))[0] + '/token.dat'
    path = os.sep.join([os.path.split(os.path.realpath(__file__))[0], 'token.dat'])
    # token文件不存在
    if not os.path.exists(path):
        lists = []
        code = -1
    else:
        lists = linecache.getlines(path)
        code = 0
    # 鉴定 token.txt 不为空
    if len(lists) != 0:
        token = lists[0].strip('\n')
        ssoToken = lists[1].strip('\n')
        # token文件有就用本地的，防止每个接口重新获取token
        if token is not None:
            return [token, ssoToken]
        url = '{0}/auth/token'.format(config.get_default('default_api_host'))
        data = {
            'access_token': ssoToken
        }
        res = https._get(url, data)
        if res is not None:
            code = res[0]['data']['code']
        else:
            code = -1
    if code != 0 or token == '':
        url = '{0}/auth/token'.format(config.get_default('default_api_host'))
        rsa = Rsa()
        data = {
            'username': username,
            'pwd': rsa.rsaEncrypt(pwd)
        }
        r = https._post(url, data)
        if r[0] is not None and r[0]['ret'] == 200 and r[0]['data']['code'] == 0:
            # 密码错误处理
            token = r[0]['data']['token']
            ssoToken = ''
            refreshToken = r[0]['data']['refresh_token']
            with open(path, mode='w+', encoding='UTF-8') as tokenFile:
                tokenFile.write(token + '\n' + ssoToken + '\n' + refreshToken)
                tokenFile.close()
        else:
            if r[0] is None:
                print('Can Not Connect Host')
            else:
                print(r[0]['data']['message'])
            exit()
    return [token, ssoToken]


def refreshToken():
    token = ''
    ssoToken = ''
    path = os.sep.join([os.path.split(os.path.realpath(__file__))[0], 'token.dat'])
    lists = linecache.getlines(path)
    refresh_token = lists[2].strip('\n')
    # 删除token文件
    os.remove(path)
    url = '{0}/auth/refresh_token'.format(config.get_default('default_api_host'))
    data = {
        'refresh_token': refresh_token,
    }
    r = https._put(url, data)
    if r[0] is not None and r[0]['ret'] == 200 and r[0]['data']['code'] == 0:
        # 密码错误处理
        token = r[0]['data']['token']
        ssoToken = ''
        refreshToken = r[0]['data']['refresh_token']
        with open(path, mode='w+', encoding='UTF-8') as tokenFile:
            tokenFile.write(token + '\n' + ssoToken + '\n' + refreshToken)
            tokenFile.close()
    elif r[0] is not None and r[0]['ret'] == 200 and r[0]['data']['code'] == 'auth.refresh_token_invalid':
        print('refresh_token is invalid, need to get token again')
        # 返回None，用于后续判断是否需要重新获取token
        return [None, None]
    else:
        if r[0] is None:
            print('Can Not Connect Host')
        else:
            print(r[0]['data']['message'])
        exit()
    return [token, ssoToken]

