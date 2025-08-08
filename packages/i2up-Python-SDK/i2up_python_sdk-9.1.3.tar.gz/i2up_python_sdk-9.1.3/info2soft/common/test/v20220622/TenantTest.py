
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.common.Tenant import Tenant
# from info2soft.common.v20200722.Tenant import Tenant
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


class TenantTestCase(unittest.TestCase):

    def testListTenant(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'search_field': '',
            'limit': 1,
            'page': 1,
            'like_args[xxx]': '',
            'where_args[xxx]': '',
            'order_by': '',
            'direction': '',
        }
        
        tenant = Tenant(a)
        r = tenant.listTenant(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Tenant', 'listTenant', body)

    def testCreateTenant(self):
        a = Auth(username, pwd)
        body = {
            'tenant_name': '',
            'display_name': '',
            'description': '',
            'enabled': 1,
        }
        
        tenant = Tenant(a)
        r = tenant.createTenant(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Tenant', 'createTenant', body)

    def testModifyTenant(self):
        a = Auth(username, pwd)
        body = {
            'display_name': '',
            'description': '',
            'enabled': 0,
            'random_str': '',
            'tenant_name': '',
        }
        id = "2"
        tenant = Tenant(a)
        r = tenant.modifyTenant(body, id)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Tenant', 'modifyTenant', body)

    def testDeleteTenant(self):
        a = Auth(username, pwd)
        body = {
            'ids': [{
            '': '',},],
        }
        
        tenant = Tenant(a)
        r = tenant.deleteTenant(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Tenant', 'deleteTenant', body)


if __name__ == '__main__':
    unittest.main()
