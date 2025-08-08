# -*- coding: utf-8 -*-


import platform

import requests
import json
from requests.auth import AuthBase

import time
import uuid
import random
import struct
import hmac
import hashlib
import urllib.parse

from info2soft.compat import is_py2, is_py3
from info2soft import config
import info2soft.common.Auth
from info2soft import __version__

_sys_info = '{0}; {1}'.format(platform.system(), platform.machine())
_python_ver = platform.python_version()

USER_AGENT = 'info2softPython/{0} ({1}; ) Python/{2}'.format(__version__, _sys_info, _python_ver)


_headers = {
    'User-Agent': USER_AGENT,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'timestamp': '',
    'Authorization': '',
    'Signature': ''
    }


def __return_wrapper(resp):
    # content type不是json，比如下载文件，则不走json处理
    if 'application/json' not in resp.headers.get('Content-type'):
        ret = {'ret': resp.status_code, 'data': resp.text}
        return ret, ResponseInfo(resp)
    # if resp.status_code != 200:
    #     return None, ResponseInfo(resp)
    resp.encoding = 'utf-8'
    # ret = resp.json(encoding='utf-8') if resp.text != '' else {}
    ret = None
    if resp.text != '':
        ret = resp.json(encoding='utf-8')
        if not ret:  # 当resp.text = '[]'时，resp.json会返回空数组，需要特别处理
            ret = {'ret': resp.status_code}
        else:
            ret['ret'] = resp.status_code
    return ret, ResponseInfo(resp)


def _post(url, data, auth=None, headers=None, head_config=None, skip_retry=False):
    try:
        src_data = data
        auth_type = 'token' if auth is None else auth.auth_type
        token = '' if auth is None else auth.token
        ak = '' if auth is None else auth.access_key
        sk = '' if auth is None else auth.secret_key
        # 3eb647b1
        data['_'] = hex(struct.unpack('<I', struct.pack('<f', random.random()))[0])[2:]

        header_config = _generate_header(auth_type, token, ak, sk, 'post', url, data['_'], data)

        if headers is not None:
            for k, v in headers.items():
                header_config.update({k: v})
        requests.packages.urllib3.disable_warnings()

        data = json.dumps(data)

        r = requests.post(
            url,
            data=data,
            auth=info2soft.common.Auth.RequestsAuth(auth) if auth is not None else None,
            headers=header_config,
            timeout=config.get_default('connection_timeout'),
            verify=False
        )
    except Exception as e:
        return None, ResponseInfo(None, e)

    ret = __return_wrapper(r)
    if (not skip_retry) and (ret[0]['ret'] == 401 or ret[0]['ret'] == 403 or r.status_code == 403):
        return _post(url, src_data, auth.refresh_token(), headers, head_config, True)
    else:
        return ret


def _get(url, params=None, auth=None, skip_retry=False):
    try:
        src_url = url
        src_params = params
        auth_type = 'token' if auth is None else auth.auth_type
        token = '' if auth is None else auth.token
        ak = '' if auth is None else auth.access_key
        sk = '' if auth is None else auth.secret_key
        # 3eb647b1
        # 处理 get 请求各种状态接口传入 **uuids 数组类型，做数据处理
        # waitDel = ''
        # if params is not None:
        #     for k, v in params.items():
        #         # 如果包含了数组形式的数据需要处理一下 url
        #         if isinstance(params[k], list):
        #             urlConnectTag = '%s%s%s' % ('&', k, '[]=')
        #             urlSub = urlConnectTag.join(params[k])
        #             urlConnectSub = '%s%s%s' % ('?', k, '[]=')
        #             url = '%s%s%s' % (url, urlConnectSub, urlSub)
        #             waitDel = k
        # if waitDel != '':
        #     params.pop(waitDel)

        _ = hex(struct.unpack('<I', struct.pack('<f', random.random()))[0])[2:]
        if params is not None:
            params['_'] = _
        else:
            params = {
                '_': _
            }

        # 用params里的数据生成完整的URL，对字典和列表类型的值作特殊处理，以保证Server端正确解析
        if params is not None:
            query_string = json_to_query_string(params)
            if query_string != '':
                url = '%s?%s' % (url, query_string)

        header_config = _generate_header(auth_type, token, ak, sk, 'get', url, _, params)

        requests.packages.urllib3.disable_warnings()
        r = requests.get(
            url,
            params=None,
            auth=info2soft.common.Auth.RequestsAuth(auth) if auth is not None else None,
            timeout=config.get_default('connection_timeout'),
            headers=header_config,
            verify=False
        )
    except Exception as e:
        return None, ResponseInfo(None, e)

    ret = __return_wrapper(r)
    if (not skip_retry) and (ret[0]['ret'] == 401 or ret[0]['ret'] == 403 or r.status_code == 403):
        return _get(src_url, src_params, auth.refresh_token(), True)
    else:
        return ret

def json_to_query_string(data, prefix=''):
    params = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix}[{key}]" if prefix else key
            params.extend(json_to_query_string(value, new_prefix))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            # 使用 key[i] 格式，否则会出现querystring里有[]，而不是[0]，导致server根据querystring解析出来的参数不一致，最终签名不一致
            new_prefix = f"{prefix}[{i}]"
            params.extend(json_to_query_string(item, new_prefix))
    else:
        # 处理基本类型（字符串、数字、布尔值等）
        if isinstance(data, bool):
            # 布尔值特殊处理，转成字符串"true"或"false"
            value = "true" if data else "false"
        elif data is None:
            value = ""
        else:
            value = str(data)
        params.append((prefix, value))

    # 如果是顶层调用，组合所有参数成查询字符串
    if not prefix:
        return urllib.parse.urlencode(params)
    return params

def _put(url, data, auth=None, headers=None, skip_retry=False):
    try:
        src_data = data
        auth_type = 'token' if auth is None else auth.auth_type
        token = '' if auth is None else auth.token
        ak = '' if auth is None else auth.access_key
        sk = '' if auth is None else auth.secret_key
        # 3eb647b1
        data['_'] = hex(struct.unpack('<I', struct.pack('<f', random.random()))[0])[2:]

        header_config = _generate_header(auth_type, token, ak, sk, 'put', url, data['_'], data)

        data = json.dumps(data)

        if headers is not None:
            for k, v in headers.items():
                header_config.update({k: v})
        requests.packages.urllib3.disable_warnings()
        r = requests.put(
            url,
            data=data,
            auth=info2soft.common.Auth.RequestsAuth(auth) if auth is not None else None,
            headers=header_config,
            timeout=config.get_default('connection_timeout'),
            verify=False
        )
    except Exception as e:
        return None, ResponseInfo(None, e)

    ret = __return_wrapper(r)
    if (not skip_retry) and (ret[0]['ret'] == 401 or ret[0]['ret'] == 403 or r.status_code == 403):
        return _put(url, src_data, auth.refresh_token(), headers, True)
    else:
        return ret


def _delete(url, data, auth=None, headers=None, skip_retry=False):
    try:
        src_data = data
        auth_type = 'token' if auth is None else auth.auth_type
        token = '' if auth is None else auth.token
        ak = '' if auth is None else auth.access_key
        sk = '' if auth is None else auth.secret_key
        # 3eb647b1
        data['_'] = hex(struct.unpack('<I', struct.pack('<f', random.random()))[0])[2:]

        header_config = _generate_header(auth_type, token, ak, sk, 'delete', url, data['_'], data)

        data = json.dumps(data)

        if headers is not None:
            for k, v in headers.items():
                header_config.update({k: v})
        requests.packages.urllib3.disable_warnings()
        r = requests.delete(
            url,
            data=data,
            auth=info2soft.common.Auth.RequestsAuth(auth) if auth is not None else None,
            headers=header_config,
            timeout=config.get_default('connection_timeout'),
            verify=False
        )
    except Exception as e:
        return None, ResponseInfo(None, e)

    ret = __return_wrapper(r)
    if (not skip_retry) and (ret[0]['ret'] == 401 or ret[0]['ret'] == 403 or r.status_code == 403):
        return _delete(url, src_data, auth.refresh_token(), headers, True)
    else:
        return ret


class _TokenAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = '{0}'.format(self.token)
        return r


def _post_with_token(url, data, token):
    return _post(url, data, _TokenAuth(token))


def _post_with_auth(url, data, auth):
    return _post(url, data, info2soft.common.Auth.RequestsAuth(auth))


# def _generate_signature(_, method, url):
#     timestamp = int(round(time.time() * 1000))
#     nonce = uuid.uuid4()
#     sign_str = method.upper() + '\n' + url + '\n' + _ + '\n' + timestamp + '\n' + nonce
#     signature = hmac.new("key", sign_str, digestmod=hashlib.sha256).digest()
#     return signature

def filter_empty(data):
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                filtered_v = filter_empty(v)
                if filtered_v:  # 只有非空时才保留
                    result[k] = filtered_v
            else:
                result[k] = v
        return result
    elif isinstance(data, list):
        result = []
        for item in data:
            if isinstance(item, (dict, list)):
                filtered_item = filter_empty(item)
                if filtered_item:  # 只有非空时才保留
                    result.append(filtered_item)
            else:
                result.append(item)
        return result
    else:
        return data

def _generate_header(auth_type='', token='', ak='', sk='', method='', url='', _='', data=None):
    timestamp = int(round(time.time() * 1000))/1000
    nonce = uuid.uuid4()
    header_config = {
        'User-Agent': USER_AGENT,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token if auth_type == 'token' else '',
        'ACCESS-KEY': ak if auth_type == 'ak' else '',
        'timestamp': str(timestamp),
        'nonce': str(nonce),
        'Signature': ''
    }
    url_parse = urllib.parse.urlsplit(url)
    sign_str = method.upper() + '\n' + url_parse.path + '\n' + _ + '\n' + str(timestamp) + '\n' + str(nonce)
    # signature = hmac.new(token, sign_str, digestmod=hashlib.sha256).hexdigest()
    # signature_bytes = ''

    sign_key = sk if auth_type == 'ak' else token

    signature_bytes = hmac.new(
        bytes(sign_key, encoding='utf-8'),
        bytes(sign_str, encoding='utf-8'),
        digestmod=hashlib.sha256
    ).digest()

    # enable_sign_enhance
    sign_fields = []
    url_params = urllib.parse.parse_qs(url_parse.query, keep_blank_values=True)
    url_params.update(data)
    if config.get_default('log_switch'):
        print(url)
        print(url_params)

    # 如果是GET方法，需要移除data里的空数组和空字典，不论是否嵌套，确保和server端处理一致（http_build_query函数）
    if method.lower() == 'get':
        data = filter_empty(data)

    if data is not None:
        for k, v in sorted(data.items(), key=lambda x: x[0]):
            if v is '' or v is None:
                continue

            if type(v) is not str:
                original_v = v
                v = json.dumps(v, separators=(',', ':'), ensure_ascii=False).replace('\"', '')

                # 如果是空字典，将大括号替换为中括号（字典内的空字典和数组内的空字典都需要替换为中括号），与Server端处理一致
                if type(original_v) is dict or type(original_v) is list:
                    v = v.replace('{}', '[]')
            sign_fields.append(str(k) + '=' + str(v))
        enhance_sign_str = '&' . join(sign_fields)
        enhance_sign_str = enhance_sign_str.replace('"', '')
        enhance_signature_bytes = hmac.new(
            bytes(sign_key or 'token', encoding='utf-8'),
            bytes(enhance_sign_str, encoding='utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        header_config['enhanceStr'] = enhance_signature_bytes.hex().lower()

    if config.get_default('log_switch'):
        print('===== enhance sign str start =====')
        print(enhance_sign_str)
        if enhance_signature_bytes:
            print(enhance_signature_bytes.hex().lower())
        print('===== enhance sign str end =====')

    signature = signature_bytes.hex().lower()

    header_config['Signature'] = signature

    return header_config


class ResponseInfo(object):
    """HTTP请求返回信息类

    该类主要是用于获取和解析各种请求后的响应包的header和body。

    """

    def __init__(self, response, exception=None):
        """用响应包和异常信息初始化ResponseInfo类"""
        self.__response = response
        self.exception = exception
        if response is None:
            self.status_code = -1
            self.text_body = None
            self.error = str(exception)
        else:
            self.status_code = response.status_code
            self.text_body = response.text
            if self.status_code >= 400:
                ret = response.json() if response.text != '' else None
                if ret is None:
                    self.error = 'unknown'
                else:
                    self.error = ret['msg'] if 'msg' in ret else 'unknown'
                # 便于知道错误定位
                print(self)

    def ok(self):
        return self.status_code == 200

    def need_retry(self):
        if self.__response is None:
            return True
        code = self.status_code
        if (code // 100 == 5 and code != 579) or code == 996:
            return True
        return False

    def connect_failed(self):
        return self.__response is None

    def __str__(self):
        if is_py2:
            return ', '.join(['%s:%s' % item for item in self.__dict__.items()]).encode('utf-8')
        elif is_py3:
            return ', '.join(['%s:%s' % item for item in self.__dict__.items()])

    def __repr__(self):
        return self.__str__()
