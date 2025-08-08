
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Client import Client
# from info2soft.common.v20200722.Client import Client
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


class ClientTestCase(unittest.TestCase):

    def testUpdateSlaveNode(self):
        a = Auth(username, pwd)
        body = {
            'config': '',
        }
        
        client = Client(a)
        r = client.updateSlaveNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'updateSlaveNode', body)

    def testGetVirtualPlatforms(self):
        a = Auth(username, pwd)
        body = {
            'npsvr_uuid': '',
        }
        
        client = Client(a)
        r = client.getVirtualPlatforms(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'getVirtualPlatforms', body)

    def testGetVirtualPlatformRules(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuids': [
            '3C334EF3',
            '3C334EF3',],
        }
        
        client = Client(a)
        r = client.getVirtualPlatformRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'getVirtualPlatformRules', body)

    def testCreateCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '65DA3916-AF53-CE70-0B47-A142414AA140',
            'result_uuid': '25DA3916-AF13-CE70-0B47-B142414AA142',
            'result': {
            'code': '0',
            'time': '10',
            'files': '100',
            'bytes': '1111111',
            'missing': '2',
            'diff': '48',
            'equal': '50',
            'erro': '',},
            'result_type': 'rep',
        }
        
        client = Client(a)
        r = client.createCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'createCompareResult', body)

    def testCollectCompareResult(self):
        a = Auth(username, pwd)
        body = {
            'code': '',
            'start_time': '',
            'files': '',
            'bytes': '',
            'missing': '',
            'diff': '',
            'erro': '',
            'equal': '',
            'task_uuid': '',
            'cc_uuid': '',
            'send_bytes': '',
            'end_time': '',
        }

        client = Client(a)
        r = client.collectCompareResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'collectCompareResult', body)

    def testUploadCompareDiffDetail(self):
        a = Auth(username, pwd)
        body = {
            'files': [],
            'missing_files': [
            'file',
            'file',],
            'diff_files': [],
            'uuid': '',
            'cc_uuid': '',
            'is_new': 0,
        }

        client = Client(a)
        r = client.uploadCompareDiffDetail(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'uploadCompareDiffDetail', body)

    def testGetDtoStorageList(self):
        a = Auth(username, pwd)
        body = {
            'cc_uuid': '',
        }

        client = Client(a)
        r = client.getDtoStorageList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Client', 'getDtoStorageList', body)


if __name__ == '__main__':
    unittest.main()
