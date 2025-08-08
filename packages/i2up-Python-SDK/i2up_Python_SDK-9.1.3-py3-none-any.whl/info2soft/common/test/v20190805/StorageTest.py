# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.common.v20181227.Storage import Storage
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
            'name': 'name',
            'type': 0,
            'bk_uuid': 'AFAFDFDF-AFAF-AFAF-AFAF-AFAFAFAFAFAF',
            'config': {
                'device_info': [
                    {
                        'alarm': {},
                    }
                ],
                'biz_grp_list': '',
                'backstore': [
                    {
                        'name': '',
                        'path': '',
                        'capacity': '',
                        'target_name': ''
                    }
                ],
            },
            'db_save_day': 1
        }
        storage = Storage(a)
        r = storage.createStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'createStorageConfig', body)

    def testModifyStorageConfig(self):
        a = Auth(username, pwd)
        body = {
            'name': 'name',
            'config': [],
            'db_save_day': 1,
        }
        storage = Storage(a)
        r = storage.modifyStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'modifyStorageConfig', body)

    def testDescribeStorageConfig(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.describeStorageConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'describeStorageConfig', body)

    def testListStorageConfig(self):
        a = Auth(username, pwd)
        body = {
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

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

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
        }
        storage = Storage(a)
        r = storage.listAvailableDevice(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listAvailableDevice', body)

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

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

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

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

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

    def testCreateVolume(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'pool_name': '',
            'volume_name': '',
            'volume_size': '',
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

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

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

    def testTempFuncName(self):
        a = Auth(username, pwd)
        body = {
        }
        storage = Storage(a)
        r = storage.tempFuncName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'tempFuncName', body)

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


if __name__ == '__main__':
    unittest.main()
