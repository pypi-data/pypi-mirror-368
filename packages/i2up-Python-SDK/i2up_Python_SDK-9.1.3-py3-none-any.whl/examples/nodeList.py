# -*- coding: utf-8 -*-
# flake8: noqa
import json
import configparser
import sys
import os

sys.path.append(r'B:\workspace\code\SDK\python-sdk')
from info2soft import config
from info2soft import Auth
from info2soft.resource.v20181227 import Node

# conf = configparser.ConfigParser()
# conf.read('C:\\Users\\Stone\\Desktop\\i2soft-i2up-python-sdk-develop\\i2up-python-sdk\\config.ini', encoding="utf-8-sig")
# appTable = json.loads(conf.get('appTable', 'value'))
# print(appTable)

## 设置控制台地址
config.set_default(None, None, None, 'https://***:58086/api', True)


username = ''
pwd = ''

auth = Auth(username, pwd, 'ak', 'aBvktc7e***', '***')
nodebody = {
    # 'limit': 1000,
    # 'page': 1,
}

node = Node(auth)

noderes, info = node.listNode(nodebody)
if noderes is not None:
    print('All is OK')
    # 格式化输出结果，提升可读性
    # Format output results to improve readability
    dumpRet = json.dumps(noderes, sort_keys=True, indent=4, separators=(',', ':'))
    print(dumpRet)
else:
    # error message in info
    print(info)
