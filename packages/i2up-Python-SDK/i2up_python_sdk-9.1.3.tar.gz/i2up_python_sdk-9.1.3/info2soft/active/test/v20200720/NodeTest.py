
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft import Node
# from info2soft.active.v20200722.Node import Node
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
    
                
class NodeTestCase(unittest.TestCase):

    def testListInactiveNodes(self):
        a = Auth(username, pwd)
        body = {
        }
        
        node = Node(a)
        r = node.listInactiveNodes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listInactiveNodes', body)

    def testListNodes(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
            'nodetype': '@pick{"name","source","backup"]}',
            'search_field': '',
            'order_by': '',
            'sort': '@pick',
            'search_value': '',
        }
        
        node = Node(a)
        r = node.listNodes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNodes', body)

    def testListNodeStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'ECe4aEFE-CF4d-2AE1-eD7A-a3dbB2eAB419',
            'BFBaebeC-AC43-E92f-0ADF-F0c71b3ABBC8',],
        }
        
        node = Node(a)
        r = node.listNodeStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNodeStatus', body)

    def testDescriptNode(self):
        a = Auth(username, pwd)
        body = {
            'registered': 1,
            'node_uuid': '750c83B6-e656-d12C-e98B-1A61675b93e4',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        node = Node(a)
        r = node.descriptNode(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'descriptNode', body)

    def testActiveNode(self):
        a = Auth(username, pwd)
        body = {
            'node_name': 'Gary Wilson',
            'address': '75.82.95.60',
            'data_port': '26804',
            'cache_dir': '/var/i2data/cache/',
            'ipctoken': '82Fa2CFD-bC93-cbBB-5Fe6-d543C88693C8',
            'log_dir': '/var/i2data/log/',
            'node_uuid': 'b719ecBa-8187-D3BE-dB9C-cd30d5802BCD',
            'registered': 1,
            'relay_node': 0,
            'source_node': 1,
            'back_node': 0,
            'active_flag': '0',
            'comment': 'string',
            'web_uuid': '0DC713bE-e93b-67dC-3DfD-34F5CDd44C9E',
            'port': {
            'iawork': '',
            'iaback': '',
            'iarelay': '',
            'iatrack': '',
            'iamsk': '',
            'iaload': '',
            'iamsg': '',
            'iagauss': '',},
        }
        
        node = Node(a)
        r = node.activeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'activeNode', body)

    def testDeleteNode(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            '95215Ac5-A4f9-bA8A-991a-D89F8EAb79e2',
            '3070f557-CACE-4Ae4-7b3e-fFC8Df9Ec0cD',],
        }
        
        node = Node(a)
        r = node.deleteNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'deleteNode', body)

    def testUpgradeNode(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        node = Node(a)
        r = node.upgradeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'upgradeNode', body)

    def testDescriptNodeDebugInfo(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '41D1C1E8-60AE-4853-9694-5599560EEB0F',
        }
        
        node = Node(a)
        r = node.descriptNodeDebugInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'descriptNodeDebugInfo', body)

    def testModifyNode(self):
        a = Auth(username, pwd)
        body = {
            'node_name': 'Helen Clark',
            'address': '246.73.219.231',
            'data_port': '26804',
            'cache_dir': '/var/i2data/cache/',
            'iptoken': 'B5E1f5fB-bAD9-DDaE-b4d1-D0a9fe46FD33',
            'logdir': '/var/i2data/log/',
            'node_uuid': 'EEdf64f4-CEf7-B62c-a26e-3b3Bc89BcFf0',
            'registered': 1,
            'relay_node': 0,
            'source_node': 1,
            'back_node': 1,
            'active_flag': '0',
            'comment': 'string',
            'web_uuid': 'a2dbD81B-8e87-bd59-cA2e-b5C9EAB738db',
            'port': {
            'iawork': '26804',
            'iaback': '26805',
            'iarelay': '26806',
            'iatrack': '26807',
            'iamask': '26808',
            'iaload': '26809',
            'iamsg': '26810',
            'iaguass': '',},
        }
        
        node = Node(a)
        r = node.modifyNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'modifyNode', body)


if __name__ == '__main__':
    unittest.main()
