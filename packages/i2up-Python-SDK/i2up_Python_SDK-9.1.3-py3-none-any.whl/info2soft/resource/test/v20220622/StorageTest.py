
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/')

import unittest
# from info2soft import Storage
from info2soft.resource.v20220622.Storage import Storage
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


class StorageTestCase(unittest.TestCase):

    def testCreateStorageConfig(self):
        a = Auth(username, pwd)
        body = {
            'name': '2.85',
            'type': 0,
            'bk_uuid': '7E36A0B7-7C9A-D310-645A-F9FF7972F13F',
            'config': {
                'device_info': [
                    {
                        'dev_mount': 'C:\\',
                        'alarms': [
                            '80',
                            '90',
                        ]
                    }
                ],
                'biz_grp_list': '',
                'backstore': [
                    {
                        'name': '',
                        'path': '',
                        'capacity': '',
                        'target_name': '',
                    }
                ],
                'db_save_day': 2,
                'mon_storage': 1
            }
        }
        
        storage = Storage(a)
        r = storage.createStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createStorageConfig', body)

    def testModifyStorageConfig(self):
        a = Auth(username, pwd)
        body = {
            'name': 'test',
            'type': 0,
            'bk_uuid': '7E36A0B7-7C9A-D310-645A-F9FF7972F13F',
            'config': {
                'mon_storage': 1,
                'db_save_day': 30,
                'device_info': [
                    {
                        'dev_used_percent': 28,
                        'dev_name': '/dev/mapper/centos-root',
                        'dev_mount': '/',
                        'dev_total': '36.97 GB',
                        'dev_free': '26.72 GB',
                        'dev_type': 'block',
                        'dev_enb_compress': 'N',
                        'dev_enb_wight': 'N',
                        'dev_save_rate': '0%',
                        'node_name': 'MTQx',
                        'node_role': '3',
                        'dev_used_size': '11006136320',
                        'alarms': [
                            '90',
                            '100',
                            '70', ],
                        'disabled': 0,
                        'name': '/',
                    },
                    {
                        'dev_used_percent': 29,
                        'dev_name': '/dev/sda1',
                        'dev_mount': '/boot',
                        'dev_total': '0.99 GB',
                        'dev_free': '871.58 MB',
                        'dev_type': 'block',
                        'dev_enb_compress': 'N',
                        'dev_enb_wight': 'N',
                        'dev_save_rate': '0%',
                        'node_name': 'MTQx',
                        'node_role': '3',
                        'dev_used_size': '149336064',
                        'alarms': [
                            '90',
                            '100',
                            '70', ],
                        'disabled': 0,
                        'name': '/boot',
                    },
                ],
                'biz_grp_list': '',
            },
            'random_str': '0289FA79-85C3-5D0B-2835-A454EF4A4237',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.modifyStorageConfig(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'modifyStorageConfig', body)

    def testDescribeStorageConfig(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.describeStorageConfig(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeStorageConfig', body)

    def testListStorageConfig(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '118',
            'search_field': 'bk_node_name',
            'limit': 1,
            'page': 1,
            'direction': '',
        }
        
        storage = Storage(a)
        r = storage.listStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listStorageConfig', body)

    def testDeleteStorageConfig(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        storage = Storage(a)
        r = storage.deleteStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteStorageConfig', body)

    def testListStorageStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'FBDDEBDE-41CC-175B-9D84-4D9693EEB6C6',
            '9f2e44De-5F21-faeb-A080-8232Df2e5A4E',],
        }
        
        storage = Storage(a)
        r = storage.listStorageStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listStorageStatus', body)

    def testUploadDeviceInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'device_info': [{
                'dev_mount': 'C:\\',
                'dev_total': '42580570112',
                'dev_free': '9151045632',
                'dev_used_percent': 20, }, ],
            'Content-Type': 'application/json',
        }
        
        storage = Storage(a)
        r = storage.uploadDeviceInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'uploadDeviceInfo', body)

    def testDescribeStorageDeviceInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '7E36A0B7-7C9A-D310-645A-F9FF7972F13F',
        }
        
        storage = Storage(a)
        r = storage.describeStorageDeviceInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeStorageDeviceInfo', body)

    def testDescribeStorageHistoryData(self):
        a = Auth(username, pwd)
        body = {
            'start': 1565076908,
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.describeStorageHistoryData(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeStorageHistoryData', body)

    def testListStorageInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'rep_uuid': 'F97B3FD5-4D5D-41EE-22A9-740A74E1E13C',
            'byte_format': 1,
        }
        
        storage = Storage(a)
        r = storage.listStorageInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listStorageInfo', body)

    def testListAvailableNode(self):
        a = Auth(username, pwd)
        body = {
        }
        
        storage = Storage(a)
        r = storage.listAvailableNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listAvailableNode', body)

    def testSwitchStorageQuota(self):
        a = Auth(username, pwd)
        body = {
            'quota_switch': 1,
            'random_str': 'A5AE270D-B6E5-A3C4-14B4-CAC997B87AB2',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.switchStorageQuota(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'switchStorageQuota', body)

    def testCreateStorageQuota(self):
        a = Auth(username, pwd)
        body = {
            'zpool_name': '2.85',
            'zfs_name': 'xxx',
            'zfs_mount_path': '',
            'zfs_quota': 1,
            'user_uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.createStorageQuota(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createStorageQuota', body)

    def testModifyStorageQuota(self):
        a = Auth(username, pwd)
        body = {
            'zpool_name': '2.85',
            'zfs_name': 'xxx',
            'zfs_mount_path': '',
            'zfs_quota': 1,
            'random_str': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        quota_uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC5"
        storage = Storage(a)
        r = storage.modifyStorageQuota(body, uuid, quota_uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'modifyStorageQuota', body)

    def testListStorageQuota(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.listStorageQuota(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listStorageQuota', body)

    def testDeleteStorageQuota(self):
        a = Auth(username, pwd)
        body = {
            'quota_uuids': [],
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.deleteStorageQuota(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteStorageQuota', body)

    def testListDevice(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listDevice(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listDevice', body)

    def testListAvailableDevice(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'config_addr': '',
        }
        
        storage = Storage(a)
        r = storage.listAvailableDevice(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listAvailableDevice', body)

    def testCreatePool(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'count': 1,
            'dev_list': [],
            'pool_name': '',
        }
        
        storage = Storage(a)
        r = storage.createPool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createPool', body)

    def testExpandPool(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'count': 1,
            'dev_list': [],
            'pool_name': '',
        }
        
        storage = Storage(a)
        r = storage.expandPool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'expandPool', body)

    def testDeletePool(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
        }
        
        storage = Storage(a)
        r = storage.deletePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deletePool', body)

    def testListPool(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listPool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listPool', body)

    def testListPoolInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': 'testpool',
        }
        
        storage = Storage(a)
        r = storage.listPoolInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listPoolInfo', body)

    def testListPoolFromNode(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }

        storage = Storage(a)
        r = storage.listPoolFromNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listPoolFromNode', body)

    def testCreateFs(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'mountpoint_path': '',
            'source_disk_size': '',
        }
        
        storage = Storage(a)
        r = storage.createFs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createFs', body)

    def testDeleteFs(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteFs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteFs', body)

    def testListFs(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'fs_name': '',
            'node_uuid': '',
            'eligible_file_system_size': 1,
        }
        
        storage = Storage(a)
        r = storage.listFs(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFs', body)

    def testCreateFsSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'snap_name': '',
        }
        
        storage = Storage(a)
        r = storage.createFsSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createFsSnapshot', body)

    def testDeleteFsSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'snap_name': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteFsSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteFsSnapshot', body)

    def testListFsSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'fs_name': '',
            'snap_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listFsSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFsSnapshot', body)

    def testCreateFsCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'snap_name': '',
            'clone_name': '',
        }
        
        storage = Storage(a)
        r = storage.createFsCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createFsCloneSnapshot', body)

    def testDeleteFsCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'clone_name': '',
        }
        
        storage = Storage(a)
        r = storage.deleteFsCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteFsCloneSnapshot', body)

    def testListFsCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'fs_name': '',
            'snap_name': '',
        }
        
        storage = Storage(a)
        r = storage.listFsCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFsCloneSnapshot', body)

    def testCreateVolume(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'volume_size': '',
            'volume_attr': 1,
        }
        
        storage = Storage(a)
        r = storage.createVolume(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createVolume', body)

    def testDeleteVolume(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteVolume(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteVolume', body)

    def testListVolume(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'volume_name': '',
            'node_uuid': '',
            'eligible_volume_size': 1,
        }
        
        storage = Storage(a)
        r = storage.listVolume(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listVolume', body)

    def testCreateVolumeSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'snap_name': '',
        }
        
        storage = Storage(a)
        r = storage.createVolumeSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createVolumeSnapshot', body)

    def testDeleteVolumeSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'snap_name': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteVolumeSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteVolumeSnapshot', body)

    def testListVolumeSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'volume_name': '',
            'snap_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listVolumeSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listVolumeSnapshot', body)

    def testCreateVolumeCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'snap_name': '',
            'clone_name': '',
        }
        
        storage = Storage(a)
        r = storage.createVolumeCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createVolumeCloneSnapshot', body)

    def testDeleteVolumeCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'clone_name': '',
        }
        
        storage = Storage(a)
        r = storage.deleteVolumeCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteVolumeCloneSnapshot', body)

    def testListVolumeCloneSnapshot(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'snap_name': '',
        }
        
        storage = Storage(a)
        r = storage.listVolumeCloneSnapshot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listVolumeCloneSnapshot', body)

    def testCreateVMDK(self):
        a = Auth(username, pwd)
        body = {
        }
        
        storage = Storage(a)
        r = storage.createVMDK(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createVMDK', body)

    def testDeleteVMDK(self):
        a = Auth(username, pwd)
        body = {
        }
        
        storage = Storage(a)
        r = storage.deleteVMDK(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteVMDK', body)

    def testCreateBackStore(self):
        a = Auth(username, pwd)
        body = {
            'name': 'name',
            'path': '/path/',
            'node_uuid': 'AFAFDFDF-AFAF-AFAF-AFAF-AFAFAFAFAFAF',
            'capacity': '100',
        }
        
        storage = Storage(a)
        r = storage.createBackStore(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createBackStore', body)

    def testDeleteBackStore(self):
        a = Auth(username, pwd)
        body = {
            'name': 'bs',
            'node_uuid': 'AFAFDFDF-AFAF-AFAF-AFAF-AFAFAFAFAFAF',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteBackStore(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteBackStore', body)

    def testListBackStore(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listBackStore(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBackStore', body)

    def testCreateAssignBackStore(self):
        a = Auth(username, pwd)
        body = {
            'name': '',
            'target': '',
            'tpg_number': '',
            'initiator': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createAssignBackStore(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createAssignBackStore', body)

    def testListAssignBackStore(self):
        a = Auth(username, pwd)
        body = {
            'path': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listAssignBackStore(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listAssignBackStore', body)

    def testListBackStoreAvailablePath(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listBackStoreAvailablePath(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBackStoreAvailablePath', body)

    def testDescribeIscsiVersion(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.describeIscsiVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeIscsiVersion', body)

    def testDescribeIscsiAuth(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.describeIscsiAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeIscsiAuth', body)

    def testCreateIscsiDiscoverAuth(self):
        a = Auth(username, pwd)
        body = {
            'userid': '',
            'password': '',
            'mutual_userid': '',
            'mutual_password': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiDiscoverAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiDiscoverAuth', body)

    def testDeleteIscsiDiscoverAuth(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiDiscoverAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiDiscoverAuth', body)

    def testCreateAutoAddPortal(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'auto_add_default_portal': 0,
        }
        
        storage = Storage(a)
        r = storage.createAutoAddPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createAutoAddPortal', body)

    def testCreateAutoAddLun(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'auto_add_mapped_luns': 0,
        }
        
        storage = Storage(a)
        r = storage.createAutoAddLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createAutoAddLun', body)

    def testDescribeAutoAddPortal(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.describeAutoAddPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeAutoAddPortal', body)

    def testDescribeAutoAddLun(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.describeAutoAddLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeAutoAddLun', body)

    def testDescribeIscsiTargetStatus(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.describeIscsiTargetStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeIscsiTargetStatus', body)

    def testListIscsiTarget(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listIscsiTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listIscsiTarget', body)

    def testCreateIscsiTarget(self):
        a = Auth(username, pwd)
        body = {
            'name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiTarget', body)

    def testDeleteIscsiTarget(self):
        a = Auth(username, pwd)
        body = {
            'name': '',
            'node_uuid': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiTarget', body)

    def testCreateIscsiInitiator(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'initiator_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiInitiator(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiInitiator', body)

    def testDeleteIscsiInitiator(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'initiator_name': '',
            'node_uuid': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiInitiator(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiInitiator', body)

    def testCreateIscsiInitiatorConnectAuth(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'initiator_name': '',
            'user_id': '',
            'password': '',
            'mutual_userid': '',
            'mutual_password': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiInitiatorConnectAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiInitiatorConnectAuth', body)

    def testCreateIscsiInitiatorLun(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'initiator_name': '',
            'backstore_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiInitiatorLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiInitiatorLun', body)

    def testDeleteIscsiInitiatorLun(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'initiator_name': '',
            'initiator_lun_no': 1,
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiInitiatorLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiInitiatorLun', body)

    def testCreateIscsiInitiatorDiscoverTarget(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'portal_address': '',
            'portal_port': 1,
            'auth_type': 1,
            'user_name': '',
            'password': '',
            'hba_name': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiInitiatorDiscoverTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiInitiatorDiscoverTarget', body)

    def testCreateIscsiInitiatorConnectTarget(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'portal_address': '',
            'portal_port': 1,
            'auth_type': 1,
            'user_name': '',
            'password': '',
            'target': '',
        }
        
        storage = Storage(a)
        r = storage.createIscsiInitiatorConnectTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createIscsiInitiatorConnectTarget', body)

    def testDeleteIscsiInitiatorConnectTarget(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'target_name': '',
            'address': '',
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiInitiatorConnectTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiInitiatorConnectTarget', body)

    def testListIscsiInitiatorPortal(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.listIscsiInitiatorPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listIscsiInitiatorPortal', body)

    def testDeleteIscsiInitiatorPortal(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'address': '',
            'port_no': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteIscsiInitiatorPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteIscsiInitiatorPortal', body)

    def testIscsiInitiatorRefreshSession(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }

        storage = Storage(a)
        r = storage.iscsiInitiatorRefreshSession(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'iscsiInitiatorRefreshSession', body)

    def testListTpg(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'target_name': '',
            'tpg_number': 1,
        }
        
        storage = Storage(a)
        r = storage.listTpg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listTpg', body)

    def testCreateTpg(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createTpg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createTpg', body)

    def testDeleteTpg(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'node_uuid': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteTpg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteTpg', body)

    def testCreateTpgConnectAuth(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'userid': '',
            'password': '',
            'mutual_userid': '',
            'mutual_password': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createTpgConnectAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createTpgConnectAuth', body)

    def testDeleteTpgConnectAuth(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.deleteTpgConnectAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteTpgConnectAuth', body)

    def testCreateTpgLun(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'target_name': '',
            'tpg_number': 1,
            'backstore_name': '',
            'name': 'name',
            'path': '/path/',
            'capacity': '100',
        }
        
        storage = Storage(a)
        r = storage.createTpgLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createTpgLun', body)

    def testDescribeTpgConnectAuth(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'target_name': '',
            'tpg_number': 1,
        }
        
        storage = Storage(a)
        r = storage.describeTpgConnectAuth(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeTpgConnectAuth', body)

    def testDeleteTpgLun(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'tpg_lun_no': 1,
            'node_uuid': '',
            'force': 1,
        }
        
        storage = Storage(a)
        r = storage.deleteTpgLun(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteTpgLun', body)

    def testCreateTpgPortal(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': '',
            'ip': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.createTpgPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createTpgPortal', body)

    def testDeleteTpgPortal(self):
        a = Auth(username, pwd)
        body = {
            'target_name': '',
            'tpg_number': 1,
            'ip': '',
            'node_uuid': '',
        }
        
        storage = Storage(a)
        r = storage.deleteTpgPortal(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteTpgPortal', body)

    def testRegisterServer(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'config_addr': '',
        }

        storage = Storage(a)
        r = storage.registerServer(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'registerServer', body)

    def testListTape(self):
        a = Auth(username, pwd)
        body = {
            'where_args[node_uuid]': '',
            'page': 1,
            'limit': 10,
            'search_value': '',
            'search_field': '',
            'where_args[pool_uuid]': '',
        }

        storage = Storage(a)
        r = storage.listTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listTape', body)

    def testScanTapes(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': 'D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
        }

        storage = Storage(a)
        r = storage.scanTapes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'scanTapes', body)

    def testCreateTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_name': '磁带库1',
            'node_uuid': 'D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'library_info': [{
            'library_sn': 'SYZZ_A',
            'library_vendor': 'STK',
            'library_product': 'L80',
            'library_revision': '0106'}],
        }

        storage = Storage(a)
        r = storage.createTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createTape', body)

    def testDescribeTape(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.describeTape(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeTape', body)

    def testModifyTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_name': '磁带库1',
            'node_uuid': 'D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'library_info': [{
            'library_sn': 'SYZZ_A',
            'library_vendor': 'STK',
            'library_product': 'L80',
            'library_revision': '0106'}],
            'random_str': 'D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storage = Storage(a)
        r = storage.modifyTape(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'modifyTape', body)

    def testDeleteTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    'AA': 'BB'
                }
            ]
        }

        storage = Storage(a)
        r = storage.deleteTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'deleteTape', body)

    def testListSlot(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '93AF0C9F-14C8-41A2-31CB-AAA0F65193FA',
            'library_sn': 'SYZZY_B'
        }

        storage = Storage(a)
        r = storage.listSlot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listSlot', body)

    def testListBkData(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
            'slot _index': '',
            'slot_barcode': '',
            'slot_tapename': '',
            'slot_tapesequence': '',
            'page_num': '0',
            'page_size': '15',
            'begin_time': '2021-04-27_00:00:12',
            'end_time': '2021-04-27_00:00:12',
            'check_rule': 0,
        }

        storage = Storage(a)
        r = storage.listBkData(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBkData', body)

    def testListBkFile(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': 'D5F704B5-09Ce-3b11-5C8A-A72fcb9d3f91',
            'library_sn': '3BEe043E-8eC1-1c9E-16B2-43BCc48DAFBA',
            'slot _index': '1',
            'slot_barcode': '142419071725852	',
            'slot_tapename': '专深里美感	',
            'slot_tapesequence': '7404652025087696	',
            'bk_index': 'index',
            'bk_path': 'path',
            'page': 1,
            'limit': 10,
        }

        storage = Storage(a)
        r = storage.listBkFile(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBkFile', body)

    def testListBusyDrive(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listBusyDrive(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBusyDrive', body)

    def testListFreeSlot(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listFreeSlot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFreeSlot', body)

    def testListBusy(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listBusy(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBusy', body)

    def testListFree(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listFree(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFree', body)

    def testListBusySlot(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listBusySlot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBusySlot', body)

    def testListBusyIEslot(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listBusyIEslot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listBusyIEslot', body)

    def testListFreeIEslot(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuid': '',
            'library_sn': '',
        }

        storage = Storage(a)
        r = storage.listFreeIEslot(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listFreeIEslot', body)

    def testEraseTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'erase',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.eraseTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'eraseTape', body)

    def testFormatTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'format',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.formatTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'formatTape', body)

    def testBrowseTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'browse',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.browseTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'browseTape', body)

    def testRebuildCatalogTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'rebuild_catalog',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.rebuildCatalogTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'rebuildCatalogTape', body)

    def testUnloadTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'unload',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.unloadTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'unloadTape', body)

    def testImportTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'import',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.importTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'importTape', body)

    def testExportTape(self):
        a = Auth(username, pwd)
        body = {
            'tape_uuids': [
                {
                    '': ''
                }
            ],
            'operate': 'export',
            'slot': {
                'slot _index': '',
                'slot_barcode': '',
                'slot_tapename': '',
                'slot_tapesequence': '',
                'new_slot_tapename': ''
            },
            'drive_index': '',
            'slot_index': '',
            'ieslot_index': '',
            'library_sn': ''
        }

        storage = Storage(a)
        r = storage.exportTape(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'exportTape', body)



if __name__ == '__main__':
    unittest.main()
