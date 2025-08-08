# -*- coding: utf-8 -*-
# flake8: noqa
# import sys
import json
from info2soft.active.v20200720.SyncRules import SyncRules
from info2soft import Auth

# sys.path.append(r'C:\python_sdk')
username = 'admin'
pwd = 'Info1234'

a = Auth(username, pwd)
body = {
            'rule_uuid': '',
        }

syncRules = SyncRules(a)
ret, info = syncRules.describeSyncRulesLoadInfo(body)


if ret is not None:
    print('All is OK')
    # 格式化输出结果，提升可读性
    # Format output results to improve readability
    dumpRet = json.dumps(ret, sort_keys=True, indent=4, separators=(',', ':'))
    print(dumpRet)
else:
    # error message in info
    print(info)


body = {
            'row_uuid': '',
            'limit': 10,
            'offset': 5
        }

r = syncRules.listRuleSyncTable(body)
print(r[0])