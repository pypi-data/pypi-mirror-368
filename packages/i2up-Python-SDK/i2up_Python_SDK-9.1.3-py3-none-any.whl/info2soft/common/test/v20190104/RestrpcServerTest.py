
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.RestrpcServer import RestrpcServer
# from info2soft.common.v20200722.RestrpcServer import RestrpcServer
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


class RestrpcServerTestCase(unittest.TestCase):

    def testListRestRpcTasks(self):
        a = Auth(username, pwd)
        body = {
            'method': 'get_rules',
            'node_uuid': '10F2C96C-EA17-ED89-C592-2AD2E50C8896',
            'node_role': '',
            'node_type': '',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.listRestRpcTasks(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'listRestRpcTasks', body)

    def testAddRestRpcLog(self):
        a = Auth(username, pwd)
        body = {
            'method': '',
            'cc_uuid': '',
            'node_uuid': '',
            'content': '',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.addRestRpcLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'addRestRpcLog', body)

    def testAddRestRpcresult(self):
        a = Auth(username, pwd)
        body = {
            'type': 'result',
            'code': 1,
            'ip': '',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.addRestRpcresult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'addRestRpcresult', body)

    def testListRestRpcCcip(self):
        a = Auth(username, pwd)
        body = {
            'method': 'get_node_mode',
            'uuid': '65E3E4A5-D089-8B6A-25F3-096F6997E3F0',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.listRestRpcCcip(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'listRestRpcCcip', body)

    def testAddRestRpcHa(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'failed_node_uuid': '',
            'new_node_uuid': '',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.addRestRpcHa(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'addRestRpcHa', body)

    def testAddRestRpcCluster(self):
        a = Auth(username, pwd)
        body = {
            'cluster_uuid': '',
            'center_node_ip': '',
        }
        
        restrpcServer = RestrpcServer(a)
        r = restrpcServer.addRestRpcCluster(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'addRestRpcCluster', body)

    def testModifyEcs(self):
        a = Auth(username, pwd)
        body = {
            'restored_uuid': '',
            'ecs_id': '',
            'code': 1,
        }

        restrpcServer = RestrpcServer(a)
        r = restrpcServer.modifyEcs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'modifyEcs', body)

    def testRegisterNodeFromNode(self):
        a = Auth(username, pwd)
        body = {
            'node_name': '',
            'os_type': 1,
            'os_user': '',
            'i2id': '',
            'cc_ip': '',
            'config_addr': '',
            'username': '',
            'password': '',
            'root': '',
            'disk_limit': '',
            'mem_limit': '',
            'disk_free_space_limit': '',
        }

        restrpcServer = RestrpcServer(a)
        r = restrpcServer.registerNodeFromNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RestrpcServer', 'registerNodeFromNode', body)


if __name__ == '__main__':
    unittest.main()
