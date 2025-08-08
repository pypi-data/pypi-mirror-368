# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.resource.v20200930 import ActiveNode
# from info2soft.resource.v20200722.ActiveNode import ActiveNode
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


class ActiveNodeTestCase(unittest.TestCase):

    def testListInactiveNodes(self):
        a = Auth(username, pwd)
        body = {
        }

        activeNode = ActiveNode(a)
        r = activeNode.listInactiveNodes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'listInactiveNodes', body)

    def testActiveNode(self):
        a = Auth(username, pwd)
        body = {
            'node_name': 'Richard Anderson',
            'address': '246.71.180.238',
            'data_port': '26804',
            'cache_dir': '/var/i2data/cache/',
            'ipctoken': 'fBbF0c14-48d9-76Cb-7eE5-c7e2Df9DbD5E',
            'log_dir': '/var/i2data/log/',
            'node_uuid': 'cefA99eb-Bd1F-EdB4-a514-B62f9C36C0EA',
            'registered': 0,
            'relay_node': 0,
            'source_node': 1,
            'back_node': 1,
            'active_flag': '0',
            'comment': 'string',
            'web_uuid': '01aBe1BC-e65e-4b92-6B20-15CdfA2ef451',
            'port': {
                'iawork': '',
                'iaback': '',
                'iarelay': '',
                'iatrack': '',
                'iamsk': '',
                'iaload': '',
                'iamsg': '',
                'iagauss': '', },
        }

        activeNode = ActiveNode(a)
        r = activeNode.activeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'activeNode', body)

    def testListNodeStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
                '4B8B5979-47Fe-4D91-F5A4-8ecccC1F622F',
                '1FAc59B3-AbEB-Ae56-df82-c1DbFC5a06D3', ],
        }

        activeNode = ActiveNode(a)
        r = activeNode.listNodeStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'listNodeStatus', body)

    def testListNodes(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
            'nodetype': '@pick{"name","source","backup"]}',
            'search_field': '',
            'order_by': '',
            'sort': '@pick{"name","address"}',
            'search_value': '',
        }

        activeNode = ActiveNode(a)
        r = activeNode.listNodes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'listNodes', body)

    def testDescriptNode(self):
        a = Auth(username, pwd)
        body = {
            'registered': 0,
            'node_uuid': 'B924b6FC-9f73-7DFC-1e83-6BD7C6E5Ed6c',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        activeNode = ActiveNode(a)
        r = activeNode.descriptNode(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'descriptNode', body)

    def testDescriptNodeDebugInfo(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '41D1C1E8-60AE-4853-9694-5599560EEB0F',
        }

        activeNode = ActiveNode(a)
        r = activeNode.descriptNodeDebugInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'descriptNodeDebugInfo', body)

    def testModifyNode(self):
        a = Auth(username, pwd)
        body = {
            'node_name': 'Kimberly Jones',
            'address': '130.220.85.13',
            'data_port': '26804',
            'cache_dir': '/var/i2data/cache/',
            'iptoken': 'B9AEc607-e7Df-bD1c-c6d7-251FA47701eD',
            'logdir': '/var/i2data/log/',
            'node_uuid': 'dAb1a3df-91D9-2CC6-e212-E7277Ec525eF',
            'registered': 1,
            'relay_node': 0,
            'source_node': 1,
            'back_node': 1,
            'active_flag': '0',
            'comment': 'string',
            'web_uuid': '4AE6ea69-4fCe-621C-36BB-5EefFC9Df9Ec',
            'port': {
                'iawork': '26804',
                'iaback': '26805',
                'iarelay': '26806',
                'iatrack': '26807',
                'iamask': '26808',
                'iaload': '26809',
                'iamsg': '26810',
                'iaguass': '', },
        }

        activeNode = ActiveNode(a)
        r = activeNode.modifyNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'modifyNode', body)

    def testDeleteNode(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
                '15E8B8E7-6DEE-c4eE-11BF-Cf4B2bECBaEb',
                '24e62a9F-dA2D-66b3-Eb9a-cFE68d3833e7', ],
        }

        activeNode = ActiveNode(a)
        r = activeNode.deleteNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'deleteNode', body)

    def testListDbs(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'type': 'all',
        }

        activeNode = ActiveNode(a)
        r = activeNode.listDbs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'listDbs', body)

    def testDescribeDbHealthInfo(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'e2153bFA-dd5A-E062-Aeef-eCdbc974D77F',
        }

        activeNode = ActiveNode(a)
        r = activeNode.describeDbHealthInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'describeDbHealthInfo', body)

    def testCheckDbLink(self):
        a = Auth(username, pwd)
        body = {
            'db_name': 'Donald Hernandez',
            'node_uuid': '321e8bB7-D5EB-6b9B-c9ec-dE8EcF0386cA',
            'db_type': 'oracle',
            'file_open_type': 'DIRECT',
            'deploy_mode': 'single',
            'log_read_type': 'file',
            'config': {
                'username': 'Barbara Clark',
                'password': '',
                'server_name': '',
                'port': 1,
                'log_read': {
                    'os_auth': 1,
                    'asm_instance': '',
                    'asm_username': '',
                    'asm_port': 1,
                    'asm_password': '12323131', },
                'filter_session': 1,
                'relay': {
                    'enable': 1,
                    'relay_node_uuid': '', },
                'remote_file_agent': {
                    'enable': 1,
                    'port': 1,
                    'compress': 'none', },
                'db_list': [{
                    'ip': '',
                    'thread': '',
                    'disable': '', }, ],
                'producer_host': '244.179.169.97',
                'producer_port': 1,
                'broker_server': [{
                    'ip': '178.79.179.35',
                    'port': 1, }, ], },
            'db_uuid': '17EdE6Fe-B6E9-cB6B-4efd-BA1de5317bAe',
        }

        activeNode = ActiveNode(a)
        r = activeNode.checkDbLink(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'checkDbLink', body)

    def testListDbStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '2666d233-82Fc-7b65-DDdC-567FadDCdedf',
        }

        activeNode = ActiveNode(a)
        r = activeNode.listDbStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'listDbStatus', body)

    def testCreateDb(self):
        a = Auth(username, pwd)
        body = {
            'db_name': 'Michael Hernandez',
            'node_uuid': '4Fd4aFf6-CEc7-b4eC-26e1-298ee2ebfdAd',
            'db_type': 'oracle',
            'file_open_type': '0',
            'deploy_mode': '0',
            'log_read_type': 'file',
            'config': {
                'username': 'Patricia Miller',
                'password': '',
                'server_name': '',
                'port': 1,
                'log_read': {
                    'os_auth': 1,
                    'asm_instance': '',
                    'asm_username': '',
                    'asm_port': 1,
                    'asm_password': '12323131', },
                'filter_session': 1,
                'relay': {
                    'enable': 1,
                    'relay_node_uuid': '', },
                'remote_file_agent': {
                    'enable': 1,
                    'port': 1,
                    'compress': 'no', },
                'db_list': [{
                    'ip': '',
                    'thread': '',
                    'disable': 1, }, ],
                'producer_host': '142.19.2.228',
                'producer_port': 1,
                'broker_server': [{
                    'ip': '248.28.78.132',
                    'port': 1, }, ],
                'authentication': 'none',
                'principal': '',
                'keytabfile': '',
                'kafka_auth_type': '',
                'kerberos_keytab_path': '',
                'kerberos_principal': '',
                'kerberos_service_name': '',
                'sasl_plain_user': '',
                'sasl_plain_pass': '',
                'sqlserver': {
                    'ip': '',
                    'port': 1,
                    'usr': '',
                    'pwd': '',
                    'db': '',
                    'dacport': '', }, },
            'db_uuid': '2cbA98c9-8Ff5-54FE-2E54-CF43bB92DaD8',
            'db_mode': '',
            'cdb': '1fb95F8e-5EEa-264f-5f1b-A65dCEef2f48',
        }

        activeNode = ActiveNode(a)
        r = activeNode.createDb(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'createDb', body)

    def testModifyDb(self):
        a = Auth(username, pwd)
        body = {
            'db_name': 'Daniel Clark',
            'db_uuid': 'b9Fc88a7-C4d9-A7b5-dCDf-4BA5Fb9Fee93',
            'node_uuid': '6d7EB9Cb-be35-86ed-eBFe-DBE53fC3FABE',
            'db_type': 'oracle',
            'file_open_type': '0',
            'deploy_mode': '0',
            'log_read_type': 'file',
            'config': {
                'username': 'Linda Walker',
                'password': '',
                'server_name': '',
                'port': 1,
                'log_read': {
                    'os_auth': 1,
                    'asm_instance': '',
                    'asm_username': '',
                    'asm_port': 1,
                    'asm_password': '12323131', },
                'filter_session': 1,
                'relay': {
                    'enable': 1,
                    'relay_node_uuid': '', },
                'remote_file_agent': {
                    'enable': 1,
                    'port': 1,
                    'compress': 'no', },
                'db_list': [{
                    'ip': '',
                    'thread': '', }, ],
                'producer_host': '77.114.125.121',
                'producer_port': 1,
                'broker_server': [{
                    'ip': '142.240.164.146',
                    'port': 1, }, ], },
            'random_str': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        activeNode = ActiveNode(a)
        r = activeNode.modifyDb(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'modifyDb', body)

    def testDescribeDbSpace(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'eD71bEDE-3cA6-bFB6-23b6-3E80C7EcFeDA',
        }

        activeNode = ActiveNode(a)
        r = activeNode.describeDbSpace(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'describeDbSpace', body)

    def testUpgradeNode(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        activeNode = ActiveNode(a)
        r = activeNode.upgradeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'upgradeNode', body)

    def testDeleteDb(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'EA44970e-b38f-Ed03-79bF-94De8f1Cfb9e',
        }

        activeNode = ActiveNode(a)
        r = activeNode.deleteDb(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'deleteDb', body)

    def testBatchCreateDbs(self):
        a = Auth(username, pwd)
        body = {
        }

        activeNode = ActiveNode(a)
        r = activeNode.batchCreateDbs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'batchCreateDbs', body)

    def testDescribeDb(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        activeNode = ActiveNode(a)
        r = activeNode.describeDb(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'describeDb', body)

    def testSwitchMaintenance(self):
        a = Auth(username, pwd)
        body = {
            'switch': 0,
            'uuid': 'bBae9dCA-f6cc-BA66-bF59-8DFc395eD094',
        }

        activeNode = ActiveNode(a)
        r = activeNode.switchMaintenance(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'switchMaintenance', body)

    def testRebuildActiveNode(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        activeNode = ActiveNode(a)
        r = activeNode.rebuildActiveNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'rebuildActiveNode', body)

    def testRefresgActiveNode(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'xxxxxxxxx',
        }

        activeNode = ActiveNode(a)
        r = activeNode.refresgActiveNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ActiveNode', 'refresgActiveNode', body)


if __name__ == '__main__':
    unittest.main()
