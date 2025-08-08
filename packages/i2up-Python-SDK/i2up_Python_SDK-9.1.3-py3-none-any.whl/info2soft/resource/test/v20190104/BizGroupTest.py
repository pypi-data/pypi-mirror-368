
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.resource.v20181227.BizGroup import BizGroup
from info2soft import Auth
from info2soft.fileWriter import write
from info2soft.compat import is_py2, is_py3

if is_py2:
    import sys
    import StringIO
    import urllib

    # reload(sys)
    sys.setdefaultencoding('utf-8')
    StringIO = StringIO.StringIO
    urlopen = urllib.urlopen
if is_py3:
    import io
    import urllib

    StringIO = io.StringIO
    urlopen = urllib.request.urlopen

username = 'admin'
pwd = 'Info1234'
    
                
class BizGroupTestCase(unittest.TestCase):

    def testCreateBizGroup(self):
        a = Auth(username, pwd)
        body = {
            'biz_grp': {
                'subtype': 0,
                'comment': '123',
                'grp_name': 'grp_name',
                'type': 1,
            }
        }
        bizGroup = BizGroup(a)
        r = bizGroup.createBizGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'createBizGroup', body)

    def testModifyBizGroup(self):
        a = Auth(username, pwd)
        body = {
            'biz_grp': {
            'comment': '12313213123',
            'grp_name': 'grp_name_Modify',
            'type': 1,
            'subtype': 0,
            'grp_uuid': "8675036C-6664-8C3E-E8F4-04022FBDBA9C"
            }
        }
        bizGroup = BizGroup(a)
        r = bizGroup.modifyBizGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'modifyBizGroup', body)

    def testDescribeBizGroup(self):
        a = Auth(username, pwd)
        body = {
            'grp_uuid': "8675036C-6664-8C3E-E8F4-04022FBDBA9C"
        }
        bizGroup = BizGroup(a)
        r = bizGroup.describeBizGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'describeBizGroup', body)

    def testDeleteBizGroup(self):
        a = Auth(username, pwd)
        body = {
            'grp_uuids': ["8675036C-6664-8C3E-E8F4-04022FBDBA9C"],
        }
        bizGroup = BizGroup(a)
        r = bizGroup.deleteBizGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'deleteBizGroup', body)

    def testListBizGroup(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'search_field': '',
            'search_value': '',
            'direction': '',
            'order_by': '',
            'page': 1,
        }
        bizGroup = BizGroup(a)
        r = bizGroup.listBizGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'listBizGroup', body)

    def testUpdateBizGroupBind(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
             '990E2F2B-9983-A734-2CD3-9D298DBB365A'
            ],
            'grp_uuid': "8675036C-6664-8C3E-E8F4-04022FBDBA9C"
        }
        bizGroup = BizGroup(a)
        r = bizGroup.updateBizGroupBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'updateBizGroupBind', body)

    def testListBizGroupBind(self):
        a = Auth(username, pwd)
        body = {
            'grp_uuid': "8675036C-6664-8C3E-E8F4-04022FBDBA9C"
        }
        bizGroup = BizGroup(a)
        r = bizGroup.listBizGroupBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'listBizGroupBind', body)

    def testListBizGroupResource(self):
        a = Auth(username, pwd)
        body = {
            'type': 1,
            'subtype': 0,
        }
        bizGroup = BizGroup(a)
        r = bizGroup.listBizGroupResource(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BizGroup', 'listBizGroupResource', body)


if __name__ == '__main__':
    unittest.main()  
