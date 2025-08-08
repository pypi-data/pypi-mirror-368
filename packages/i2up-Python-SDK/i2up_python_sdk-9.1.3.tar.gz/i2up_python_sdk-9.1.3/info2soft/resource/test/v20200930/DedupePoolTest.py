
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20200930.DedupePool import DedupePool
# from info2soft.resource.v20200722.DedupePool import DedupePool
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


class DedupePoolTestCase(unittest.TestCase):

    def testCreateDedupePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_name': '',
            'node_uuid': '',
            'server_port': 1,
            'time_out': 1,
            'block_size': 1,
            'slice_size': 1,
            'hash_path': [],
            'index_path': [],
            'data_path': [],
            'compress': 1,
            'encrypt': 1,
            'secret_key': '',
            'encrypt_switch': 0,
            'ssd_mode': 0,
        }
        
        dedupePool = DedupePool(a)
        r = dedupePool.createDedupePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'createDedupePool', body)

    def testModifyDedupePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuid': '',
            'random_str': '',
            'index_path': [],
            'data_path': [],
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dedupePool = DedupePool(a)
        r = dedupePool.modifyDedupePool(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'modifyDedupePool', body)

    def testDescribeDedupePool(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dedupePool = DedupePool(a)
        r = dedupePool.describeDedupePool(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'describeDedupePool', body)

    def testDedupePoolList(self):
        a = Auth(username, pwd)
        body = {
        }
        
        dedupePool = DedupePool(a)
        r = dedupePool.dedupePoolList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'dedupePoolList', body)

    def testDeleteDedupePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'force': 1,
            'del_data': 1,
        }
        
        dedupePool = DedupePool(a)
        r = dedupePool.deleteDedupePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'deleteDedupePool', body)

    def testListDedupePoolStatus(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
        }
        
        dedupePool = DedupePool(a)
        r = dedupePool.listDedupePoolStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'listDedupePoolStatus', body)

    def testStartDedupePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'operate': '',
        }
        
        dedupePool = DedupePool(a)
        r = dedupePool.startDedupePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'startDedupePool', body)

    def testStopDedupePool(self):
        a = Auth(username, pwd)
        body = {
            'pool_uuids': [],
            'operate': '',
        }

        dedupePool = DedupePool(a)
        r = dedupePool.stopDedupePool(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DedupePool', 'stopDedupePool', body)


if __name__ == '__main__':
    unittest.main()
