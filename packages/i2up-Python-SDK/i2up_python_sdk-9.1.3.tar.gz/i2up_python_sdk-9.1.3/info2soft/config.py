# -*- coding: utf-8 -*-

# 数据 Host
API_HOST = 'https://192.168.254.143:58086/api'
API_HOST_WEBAPI = 'https://192.168.254.143:58086/api/vers/v3'
# API_HOST = ''

_config = {
    'default_api_host': API_HOST,           # i2up 分支
    'webapi_api_host': API_HOST_WEBAPI,     # webapi 分支
    'connection_timeout': 30,               # 链接超时为时间为30s
    'connection_retries': 3,                # 链接重试次数为3次
    'connection_pool': 10,                  # 链接池个数为10
    'log_switch': False,                         # 日志开关           
}


def get_default(key):
    return _config[key]

def set_default(
        connection_retries=None, connection_pool=None,
        connection_timeout=None, default_api_host=None, log_switch=False):
    if default_api_host:
        _config['default_api_host'] = default_api_host
    if connection_retries:
        _config['connection_retries'] = connection_retries
    if connection_pool:
        _config['connection_pool'] = connection_pool
    if connection_timeout:
        _config['connection_timeout'] = connection_timeout
    if log_switch:
        _config['log_switch'] = log_switch
