
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.resource.v20200930 import NodeProxy
# from info2soft.resource.v20200722.NodeProxy import NodeProxy
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


class NodeProxyTestCase(unittest.TestCase):

    def testCreateNodeProxy(self):
        a = Auth(username, pwd)
        body = {
            'proxy_addr': '',
            'proxy_port': '',
        }
        
        nodeProxy = NodeProxy(a)
        r = nodeProxy.createNodeProxy(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeProxy', 'createNodeProxy', body)

    def testListNodeProxy(self):
        a = Auth(username, pwd)
        body = {
            'search_field': '',
            'search_value': '',
        }
        
        nodeProxy = NodeProxy(a)
        r = nodeProxy.listNodeProxy(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeProxy', 'listNodeProxy', body)

    def testDescribeNodeProxy(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        nodeProxy = NodeProxy(a)
        r = nodeProxy.describeNodeProxy(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeProxy', 'describeNodeProxy', body)

    def testModifyNodeProxy(self):
        a = Auth(username, pwd)
        body = {
            'proxy_addr': '',
            'proxy_port': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        nodeProxy = NodeProxy(a)
        r = nodeProxy.modifyNodeProxy(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeProxy', 'modifyNodeProxy', body)

    def testDeleteNodeProxy(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        nodeProxy = NodeProxy(a)
        r = nodeProxy.deleteNodeProxy(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeProxy', 'deleteNodeProxy', body)


if __name__ == '__main__':
    unittest.main()
