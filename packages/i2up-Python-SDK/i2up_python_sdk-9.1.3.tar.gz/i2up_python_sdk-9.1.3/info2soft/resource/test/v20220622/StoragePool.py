
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.resource.v20220622.StoragePool import StoragePool
# from info2soft.resource.v20200722.StoragePool import StoragePool
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


class StoragePoolTestCase(unittest.TestCase):

    def testCreateStoragePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'pool_type': '',
            'ip': '',
            'disk_list': [{
            'name': '',
            'size': '',
            'type': '',},],
            'capacity': '',
        }
        
        storagePool = StoragePool(a)
        r = storagePool.createStoragePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'createStoragePool', body)

    def testModifyStoragePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'pool_type': '',
            'ip': '',
            'disk_list': [{
            'name': '',
            'size': '',
            'type': '',},],
            'capacity': '',
            'random_str': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storagePool = StoragePool(a)
        r = storagePool.modifyStoragePool(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'modifyStoragePool', body)

    def testStoragePoolList(self):
        a = Auth(username, pwd)
        body = {
            'page': '',
            'limit': '',
        }
        
        storagePool = StoragePool(a)
        r = storagePool.storagePoolList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'storagePoolList', body)

    def testDescribeStoragePool(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        storagePool = StoragePool(a)
        r = storagePool.describeStoragePool(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'describeStoragePool', body)

    def testDeleteStoragePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'force': 1,
        }
        
        storagePool = StoragePool(a)
        r = storagePool.deleteStoragePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'deleteStoragePool', body)

    def testListStoragePoolStatus(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
        }
        
        storagePool = StoragePool(a)
        r = storagePool.listStoragePoolStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'listStoragePoolStatus', body)

    def testAvailablePoolMemberList(self):
        a = Auth(username, pwd)
        body = {
            'config_addr': '',
            'pool_type': 'BlockStorage',
            'storage_conf_ip': '',
        }

        storagePool = StoragePool(a)
        r = storagePool.availablePoolMemberList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'availablePoolMemberList', body)

    def testListHbaInfo(self):
        a = Auth(username, pwd)
        body = {
            'ip': '',
        }

        storagePool = StoragePool(a)
        r = storagePool.listHbaInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'listHbaInfo', body)

    def testDeleteFcTarget(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuid': '',
            'wwpn': '',
            'force': 1,
        }

        storagePool = StoragePool(a)
        r = storagePool.deleteFcTarget(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'deleteFcTarget', body)

    def testResetStoragePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'operate': '',
            'add_disk_list': [{
            'name': '/dev/sdb',
            'size': 2000398934016,
            'type': 'disk'}],
        }

        storagePool = StoragePool(a)
        r = storagePool.resetStoragePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'resetStoragePool', body)

    def testExtendStoragePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'operate': '',
            'add_disk_list': [{
            'name': '/dev/sdb',
            'size': 2000398934016,
            'type': 'disk'}],
        }

        storagePool = StoragePool(a)
        r = storagePool.extendStoragePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'StoragePool', 'extendStoragePool', body)


if __name__ == '__main__':
    unittest.main()
