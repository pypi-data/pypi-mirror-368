
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
# from info2soft import VirtualizationSupport
from info2soft.resource.v20200930.VirtualizationSupport import VirtualizationSupport
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


class VirtualizationSupportTestCase(unittest.TestCase):

    def testCreateVp(self):
        a = Auth(username, pwd)
        body = {
            'comment': '',
            'config_addr': '192.168.72.75',
            'config_port': 58083,
            'os_pwd': '12345678',
            'os_usr': 'root',
            'vp_addr': '192.168.88.107',
            'vp_name': 'test',
            'vp_type': 0,
            'bind_lic_list': [],
            'biz_grp_list': [],
            'use_credential': 0,
            'cred_uuid': '',
            'is_drill': 1,
            'drill_config': {
            'proxy_name': '',
            'proxy_ip': '',
            'proxy_mask': '',
            'proxy_gw': '',
            'new_hostname': '',
            'new_ds': '',
            'new_dc': '',
            'new_dcmor': '',
            'network_name': '',
            'network_id': '',},
            'is_backup_center': 1,
            'cc_ip_uuid': '',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVp', body)

    def testDescribeVp(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVp', body)

    def testModifyVp(self):
        a = Auth(username, pwd)
        body = {
            'comment': '',
            'config_addr': '192.168.72.75',
            'config_port': 58083,
            'os_pwd': '12345678',
            'os_usr': 'root',
            'vp_addr': '192.168.88.107',
            'vp_name': 'test1',
            'vp_type': 0,
            'bind_lic_list': [],
            'biz_grp_list': [],
            'random_str': '11111111-1111-1111-1111-111111111111',
            'use_credential': 0,
            'cred_uuid': '',
            'is_drill': 1,
            'drill_config': {
            'proxy_name': '',
            'proxy_ip': '',
            'proxy_mask': '',
            'proxy_gw': '',
            'new_hostname': '',
            'new_ds': '',
            'new_dc': '',
            'new_dcmor': '',
            'network_name': '',
            'network_id': '',},
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVp', body)

    def testListVp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVp', body)

    def testListVpStatus(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpStatus', body)

    def testUpdateDataAgentVp(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'update_data_agent',
            'vp_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.updateDataAgentVp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'updateDataAgentVp', body)

    def testDeleteVp(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVp', body)

    def testListVM(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
            'id': '',
            'view_type': '',
            'search_name': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVM(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVM', body)

    def testDescribeVpAttribute(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpAttribute(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpAttribute', body)

    def testListBakVer(self):
        a = Auth(username, pwd)
        body = {
            'bk_path': 'H:\\vp_bk5\\test2_BAK_vm-11880_192.168.88.22\\',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listBakVer(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listBakVer', body)

    def testListBakVerInfo(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'bk_path': 'H:\\vp_bk5\\testRC1_BAK_99_192.168.85.139',
            'ver_sig': 'A59DB76E-E33D-4E22-BB08-59723B1FC539',
            'group_uuid': '',
            'time': '2019-01-07_13-10-45',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listBakVerInfo(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listBakVerInfo', body)

    def testListDatastoreFile(self):
        a = Auth(username, pwd)
        body = {
            'dir_file': '/',
            'ds_name': 'datastore107（1）',
            'dc_name': 'ha-datacenter',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDatastoreFile(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDatastoreFile', body)

    def testListDatacenter(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDatacenter(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDatacenter', body)

    def testListDatacenterHost(self):
        a = Auth(username, pwd)
        body = {
            'dc_name': 'ha-datacenter',
            'dc_mor': 'ha-datacenter',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDatacenterHost(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDatacenterHost', body)

    def testListDatastore(self):
        a = Auth(username, pwd)
        body = {
            'host_name': 'dev-esxi.6.6.6',
            'path': '/',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDatastore(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDatastore', body)

    def testListDatastoreInfo(self):
        a = Auth(username, pwd)
        body = {
            'ds_name': 'datastore107（1）',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDatastoreInfo(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDatastoreInfo', body)

    def testCreateDatastore(self):
        a = Auth(username, pwd)
        body = {
            'host_name': 'dev-esxi.6.6.6',
            'path': 'C:\\abc\\',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createDatastore(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createDatastore', body)

    def testListVmDisk(self):
        a = Auth(username, pwd)
        body = {
            'vm_ref': '123',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVmDisk(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVmDisk', body)

    def testListNetwork(self):
        a = Auth(username, pwd)
        body = {
            'host_name': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listNetwork(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listNetwork', body)

    def testDrilConfigInfo(self):
        a = Auth(username, pwd)
        body = {
            'vp_addr': '',
            'vp_type': '',
            'use_credential': '',
            'cred_uuid': '',
            'os_usr': '',
            'os_pwd': '',
            'config_addr': '',
            'config_port': 1,
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.drilConfigInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'drilConfigInfo', body)

    def testImportVmIpMapping(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': '',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.importVmIpMapping(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'importVmIpMapping', body)

    def testListNetworkInfo(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': '',
            'vm_id': '',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listNetworkInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listNetworkInfo', body)

    def testTgtVmStatusInfo(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': '',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.tgtVmStatusInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'tgtVmStatusInfo', body)

    def testListPlatformStorage(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': 'FC151595-EB90-86F5-B659-CA787753CA5D',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listPlatformStorage(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listPlatformStorage', body)

    def testPlatformAuthorize(self):
        a = Auth(username, pwd)
        body = {
            'vp_storage': [{
            'uuid': 'FC151595-EB90-86F5-B659-CA787753CA5D',
            'enabled': 0,
            'capacity': '10',},],
            'vp_uuid': 'DC151595-EB90-86F5-B659-CA787751CA5D',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.platformAuthorize(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'platformAuthorize', body)

    def testListVpStorage(self):
        a = Auth(username, pwd)
        body = {
            "where_args['enabled']": '1',
        }
        
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpStorage(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpStorage', body)

    def testDl(self):
        a = Auth(username, pwd)
        body = {
            'type': 'vm_ip_csv',
            'vp_uuid': 'DC151595-EB90-86F5-B659-CA787751CA5D',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.dl(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'dl', body)

    def testListBakVerByIp(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': '',
            'bk_path': '',
            'config_addr': '',
            'config_port': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listBakVerByIp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listBakVerByIp', body)

    def testListBakVerInfoByIp(self):
        a = Auth(username, pwd)
        body = {
            'config_addr': '',
            'config_port': '',
            'time': '',
            'ver_sig': '',
            'bk_uuid': '',
            'bk_path': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listBakVerInfoByIp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listBakVerInfoByIp', body)

    def testTestNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '5765E77A-C658-9AF1-83D0-1897B8A5850E',
            'cred_uuid': '4165E77A-C658-9AF1-83D0-1897B8A5850E',
            'trans_type': 'FTP',
            'vp_uuid': '6765E77A-C658-9AF1-83D0-1897B8A5850E',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.testNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'testNode', body)

    def testGetTargetVmInfo(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'group_uuid': '',
            'rule_type': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.getTargetVmInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'getTargetVmInfo', body)

    def testListDiskType(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': '',
            'region_id': '',
            'project_id': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listDiskType(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listDiskType', body)

    def testDiscoveryVm(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': '',
            'match_policy': {
            'vm_name': [{
            'type': '',
            'value': '',},],
            'location': [{
            'type': '',
            'value': '',},],
            'folder': [{
            'type': '',
            'value': '',},],},
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.discoveryVm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'discoveryVm', body)


if __name__ == '__main__':
    unittest.main()
