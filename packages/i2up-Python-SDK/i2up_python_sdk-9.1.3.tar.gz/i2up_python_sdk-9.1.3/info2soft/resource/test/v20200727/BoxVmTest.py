
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft import BoxVm
# from info2soft.resource.v20200722.BoxVm import BoxVm
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
pwd = '12345678'
    
                
class BoxVmTestCase(unittest.TestCase):

    def testTemplateList(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': '',
        }
        
        boxVm = BoxVm(a)
        r = boxVm.templateList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'templateList', body)

    def testCreateBoxVm(self):
        a = Auth(username, pwd)
        body = {
            'vm_name': 'win2008',
            'bk_uuid': 'xxxxx',
            'template': 'win2008r2',
            'disk': [{
            'name': 'D',
            'size': '1',},{
            'name': 'D',
            'size': '1',},],
            'hardware': {
            'cpu': '2',
            'mem': '4',},
            'network': {
            'ip': '192.168.20.8',
            'gateway': '192.168.1.10',
            'netmask': '255.255.192.0',},
        }
        
        boxVm = BoxVm(a)
        r = boxVm.createBoxVm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'createBoxVm', body)

    def testBoxVmList(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'page': 1,
            'search_value': '',
            'search_field': '',
        }
        
        boxVm = BoxVm(a)
        r = boxVm.boxVmList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'boxVmList', body)

    def testDescribeBoxVm(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        boxVm = BoxVm(a)
        r = boxVm.describeBoxVm(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'describeBoxVm', body)

    def testDeleteBoxVm(self):
        a = Auth(username, pwd)
        body = {
            'vm_uuids': [],
        }
        
        boxVm = BoxVm(a)
        r = boxVm.deleteBoxVm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'deleteBoxVm', body)

    def testListBoxVmStatus(self):
        a = Auth(username, pwd)
        body = {
            'vm_uuids': [],
        }
        
        boxVm = BoxVm(a)
        r = boxVm.listBoxVmStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'listBoxVmStatus', body)

    def testRegisterBoxVm(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'register',
            'vm_uuids': [],
        }

        boxVm = BoxVm(a)
        r = boxVm.registerBoxVm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BoxVm', 'registerBoxVm', body)


if __name__ == '__main__':
    unittest.main()
