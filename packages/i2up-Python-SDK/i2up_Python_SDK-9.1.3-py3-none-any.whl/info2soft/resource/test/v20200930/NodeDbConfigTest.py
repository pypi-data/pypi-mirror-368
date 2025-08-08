
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20200930.NodeDbConfig import NodeDbConfig
# from info2soft.resource.v20200722.NodeDbConfig import NodeDbConfig
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


class NodeDbConfigTestCase(unittest.TestCase):

    def testNodeGetDatabaseInstances(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'os_user': '',
            'os_passwd': '',
            'db_type': 1,
        }
        
        nodeDbConfig = NodeDbConfig(a)
        r = nodeDbConfig.nodeGetDatabaseInstances(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeDbConfig', 'nodeGetDatabaseInstances', body)

    def testCreateNodeDbConfig(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'db_type': '',
            'config_sw': '',
            'os_user': '',
            'os_passwd': '',
            'instance_info': [],
        }
        
        nodeDbConfig = NodeDbConfig(a)
        r = nodeDbConfig.createNodeDbConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeDbConfig', 'createNodeDbConfig', body)

    def testListNodeDbConfig(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'db_type': 'oracle',
        }
        
        nodeDbConfig = NodeDbConfig(a)
        r = nodeDbConfig.listNodeDbConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NodeDbConfig', 'listNodeDbConfig', body)


if __name__ == '__main__':
    unittest.main()
