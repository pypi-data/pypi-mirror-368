
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.resource.v20181227.Node import Node
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

    def testAuthNode(self):
        a = Auth(username, pwd)
        body = {
            'proxy_switch': 0,
            'config_addr': '192.168.72.76',
            'config_port': 26821,
            'node_uuid': '',
            'os_user': 'chenky',
            'os_pwd': '123qwe',
            'i2id': '',
            'use_credential': 0,
            'cred_uuid': '',
        }

        node = Node(a)
        r = node.authNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'authNode', body)

    def testListNodePackageList(self):
        a = Auth(username, pwd)
        body = {
            'for_download': 1,
        }

        node = Node(a)
        r = node.listNodePackageList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNodePackageList', body)

    def testCheckCapacity(self):
        a = Auth(username, pwd)
        body = {
            'config_port': '26821',
            'cache_path': 'C:\\Program Files (x86)\\info2soft\\node\\cache\\',
            'config_addr': '192.168.72.76',
        }
        node = Node(a)
        r = node.checkCapacity(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'checkCapacity', body)

    def testListVg(self):
        a = Auth(username, pwd)
        body = {
            'config_port': '26821',
            'config_addr': '192.168.72.76',
        }
        node = Node(a)
        r = node.listVg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listVg', body)

    def testListHostInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_type': 1,
            'config_addr': '',
        }

        node = Node(a)
        r = node.listHostInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listHostInfo', body)

    def testCheckNodeOnline(self):
        a = Auth(username, pwd)
        body = {
            'port': '26821',
            'ip': '192.168.72.76',
        }
        node = Node(a)
        r = node.checkNodeOnline(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'checkNodeOnline', body)

    def testBatchSearchByPort(self):
        a = Auth(username, pwd)
        body = {
            'ip': '',
            'port_start': 1,
            'port_end': 1,
        }

        node = Node(a)
        r = node.batchSearchByPort(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'batchSearchByPort', body)

    def testListNodeBindEcs(self):
        a = Auth(username, pwd)
        body = {
            'config_addr': '192.168.72.76',
            'config_port': '26821',
            'platform_uuid': '',
        }

        node = Node(a)
        r = node.listNodeBindEcs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNodeBindEcs', body)

    def testCreateNode(self):
        a = Auth(username, pwd)
        body = {
            'node': {
                'bak_client_max': '100',
                'cloud_type': '0',
                'bak_root': '',
                'monitor_switch': 0,
                'node_role': '3',
                'mem_limit': '819',
                'config_port': '26821',
                'mon_save_day': '5',
                'vg': '',
                'os_type': 1,
                'log_path': 'C:\\Program Files (x86)\\info2soft\\node\\log\\',
                'mon_data_path': 'C:\\Program Files (x86)\\info2soft\\node\\log\\',
                'comment': '',
                'rep_path': [],
                'bak_user_max': '100',
                'cache_path': 'C:\\Program Files (x86)\\info2soft\\node\\cache\\',
                'db_save_day': '3',
                'proxy_switch': 0,
                'data_addr': '192.168.72.76',
                'node_name': 'N4_72.76',
                'config_addr': '192.168.72.76',
                'mon_send_interval': '10',
                'disk_limit': '10240',
                'reboot_sys': '0',
                'bind_lic_list': [],
                'security_check': 0,
                'os_user': 'Kyran',
                'bak_service_type': '',
                'en_snap_switch': 0,
                'rep_excl_path': [],
                'biz_grp_list': [],
                'i2id': '',
            },
        }
        node = Node(a)
        r = node.createNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'createNode', body)

    def testModifyNode(self):
        a = Auth(username, pwd)
        body = {
            'node': {
               "monitor_switch": 0,
               "mon_send_interval": "10",
               "mon_data_path": None,
               "mon_save_day": "5",
               "db_save_day": "3",
               "chart_config": "0",
               "info": None,
               "created_at": "1546827340",
               "updated_at": None,
               "username": "admin",
               "id": "14",
               "bak_client_max": "100",
               "bak_root": "",
               "bak_service_type": "",
               "bak_user_max": "100",
               "bind_lic_list": [],
               "cache_path": "C:\\Program Files (x86)\\info2soft\\node\\cache\\",
               "cls_disk": None,
               "cls_node": None,
               "cls_is_local": None,
               "comment": "",
               "config_addr": "192.168.72.76",
               "config_port": "26821",
               "create_time": "1546827340",
               "data_addr": "192.168.72.76",
               "data_port": "26831",
               "disk_limit": "10240",
               "en_snap_switch": 0,
               "log_path": "C:\\Program Files (x86)\\info2soft\\node\\log\\",
               "mem_limit": "819",
               "node_name": "N4_72.76Modify",
               "node_role": "3",
               "node_type": 0,
               "node_uuid": "35E926D9-53D5-40E0-AD81-8711006DCB23",
               "os_version": "Microsoft Windows 10/x64 Edition",
               "os_type": 1,
               "os_user": "Kyran",
                'os_pwd': 'EnEyGDJF==',
               "phy_type": 2,
               "proxy_switch": 0,
               "random_str": "F3BE9F6C-9896-D4A4-2CBD-CB6D7313078B",
               "rep_excl_path": [],
               "rep_path": [
                "/"
               ],
               "security_check": 0,
               "status": None,
               "tc_uuid": None,
               "user_uuid": "1BCFCAA3-E3C8-3E28-BDC5-BE36FDC2B5DC",
               "vg": "",
               "hardware_code": None,
               "i2id": "",
               "biz_grp_list": [],
               "biz_grp_name": [],
               "allow_modify_cache_path": 1
              },
        }
        node = Node(a)
        r = node.modifyNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'modifyNode', body)

    def testDescribeNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '990E2F2B-9983-A734-2CD3-9D298DBB365A'
        }
        node = Node(a)
        r = node.describeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'describeNode', body)

    def testCreateBatchNode(self):
        a = Auth(username, pwd)
        body = {
            'base_info_list': [
                {
                    'os_pwd': '123qwe',
                    'os_user': 'chenky',
                    'config_port': '26821',
                    'config_addr': '192.168.72.76',
                    'node_name': 'N4_72.76',
                }
            ],
            'node': {
                'mem_limit': '819',
                'bind_lic_list': [],
                'disk_limit': '10240',
                'monitor_interval': '10',
                'node_role': '3',
                'monitor_switch': 0,
                'moni_log_keep_node': '5',
                'moni_log_keep_server': '3',
                'security_check': 0,
                'biz_grp_list': []
            },
        }
        node = Node(a)
        r = node.createBatchNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'createBatchNode', body)

    def testDescribeDeviceInfo(self):
        a = Auth(username, pwd)
        body = {
            "node_uuid": "990E2F2B-9983-A734-2CD3-9D298DBB365A",
        }
        node = Node(a)
        r = node.describeDeviceInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'describeDeviceInfo', body)

    def testListNode(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'search_field': '',
            'limit': 10,
            'page': 1,
            'type': '',
            # 'like_args[xxx]': '',
            # 'where_args[xxx]': '',
            'filter_by_biz_grp': '',
            'order_by': '',
            'direction': '',
        }
        node = Node(a)
        r = node.listNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNode', body)

    def testUpgradeNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuids': ["990E2F2B-9983-A734-2CD3-9D298DBB365A"],
            'operate': 'upgrade',
        }
        node = Node(a)
        r = node.upgradeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'upgradeNode', body)

    def testMaintainNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuids': ["990E2F2B-9983-A734-2CD3-9D298DBB365A"],
            'operate': 'maintain',
        }
        node = Node(a)
        r = node.upgradeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'maintainNode', body)

    def testListNodeStatus(self):
        a = Auth(username, pwd)
        body = {
            'node_uuids': ["990E2F2B-9983-A734-2CD3-9D298DBB365A"],
        }
        node = Node(a)
        r = node.listNodeStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listNodeStatus', body)

    def testDeleteNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuids': ['990E2F2B-9983-A734-2CD3-9D298DBB365A',],
        }
        node = Node(a)
        r = node.deleteNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'deleteNode', body)

    def testNode(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'page': 1,
            'type': 1,
        }

        node = Node(a)
        r = node.node(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'node', body)

    def testAddSlaveNode(self):
        a = Auth(username, pwd)
        body = {
            'proxy_switch': '0',
            'config_addr': '',
            'config_port': 1,
            'i2id': '',
            'os_pwd': 'yAZe2Hx6/dCL8GnjiRaro/mayqD24i3bMwZLtRXrHlRDIijGDcNKTqSK4IL91YIaqAGaOpUbnTr+y6VPgJ4UXJQset0se7bQgVrRjVncNeiVNCNyAzLktWYMMGKOWekw5uD2MOVEHhbknG0ZSuFXyywFEG9JTntNerCae7RSI6u2c3kRBCyqbdPc9osMK8YL9ZRqiIE/4K1+BomG9q1RwNEJhDcm/OaMxJCPHANNTImBWWv+Ir3qt20jjv1Fx7of2Fgb14Sj4TwGb7ESrbMiL/fblrfGl+rc6koNucEIRdT+aje+F47pKu4mknubWZ1wo+W2p/yaKyqfzTfeDFJtFQ==',
            'os_user': 'administrator',
            'use_credential': 1,
            'cred_uuid': '',
            'bind_lic_list': [],
            'biz_grp_list': [],
            'comment': '',
        }

        node = Node(a)
        r = node.addSlaveNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'addSlaveNode', body)

    def testNodeGetOracleInfo(self):
        a = Auth(username, pwd)
        body = {
            'username': '',
            'password': '',
            'sqlplus_path': '',
            'sid': '',
            'timeout': '',
            'port': '',
            'bk_uuid': '',
        }

        node = Node(a)
        r = node.nodeGetOracleInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'nodeGetOracleInfo', body)

    def testNodeGetMysqlInfo(self):
        a = Auth(username, pwd)
        body = {
            'username': '',
            'password': '',
            'mysql_path': '',
            'timeout': '',
            'port': '',
            'bk_uuid': '',
        }

        node = Node(a)
        r = node.nodeGetMysqlInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'nodeGetMysqlInfo', body)

    def testDataIpList(self):
        a = Auth(username, pwd)
        body = {
            'node_uuids': [],
        }

        node = Node(a)
        r = node.dataIpList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'dataIpList', body)

    def testModifyDataIp(self):
        a = Auth(username, pwd)
        body = {
            'data_ip_list': [{
            'uuid': 'A7EC7CF9-FCA2-D467-ECD6-E028AA9C8319',
            'data_ip': '172.20.15.121'}],
            'node_uuid': 'D6EC7CF9-FCA2-D467-ECD6-E028AA9C8319',
        }

        node = Node(a)
        r = node.modifyDataIp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'modifyDataIp', body)

    def testDescribeDriverLetter(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        node = Node(a)
        r = node.describeDriverLetter(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'describeDriverLetter', body)

    def testListHbaInfo(self):
        a = Auth(username, pwd)
        body = {
            'config_addr': '',
            'config_port': '',
            'proxy_switch': 1,
            'i2id': '',
        }

        node = Node(a)
        r = node.listHbaInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listHbaInfo', body)

    def testCheckUnbindEcs(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }

        node = Node(a)
        r = node.checkUnbindEcs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'checkUnbindEcs', body)

    def testGetNodeVersion(self):
        a = Auth(username, pwd)
        body = {
            'ip': '',
            'port': 1,
            'add': 1,
            'cls_uuid': '',
        }

        node = Node(a)
        r = node.getNodeVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'getNodeVersion', body)

    def testActiveNode(self):
        a = Auth(username, pwd)
        body = {
            'list': [{
            'node_uuid': '',
            'bind_lic_list': [],},],
        }

        node = Node(a)
        r = node.activeNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'activeNode', body)

    def testListWaitingActiveNode(self):
        a = Auth(username, pwd)
        body = {
        }

        node = Node(a)
        r = node.listWaitingActiveNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'listWaitingActiveNode', body)

    def testDownloadNodeInstallScript(self):
        a = Auth(username, pwd)
        body = {
            'os_type': 0,
        }

        node = Node(a)
        r = node.downloadNodeInstallScript(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'downloadNodeInstallScript', body)

    def testGetNodePackageUrl(self):
        a = Auth(username, pwd)
        body = {
            'os_type': 1,
        }

        node = Node(a)
        r = node.getNodePackageUrl(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Node', 'getNodePackageUrl', body)


if __name__ == '__main__':
    unittest.main()  
