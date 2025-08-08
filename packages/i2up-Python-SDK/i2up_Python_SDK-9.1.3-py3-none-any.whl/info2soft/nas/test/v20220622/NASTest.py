
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.nas.v20220622.NAS import NAS
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
    
                
class NASTestCase(unittest.TestCase):

    def testCreateNAS(self):
        a = Auth(username, pwd)
        body = {
            'compress': '',
            'secret_key': '',
            'wk_list': [
                {
                    'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                    'wk_path': 'E:\\nas\\',
                }
            ],
            'nas_type': '0',
            'sync_path': '',
            'encrypt_switch': '0',
            'band_width': '',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'bk_path': 'E:\\t\\',
            'sync_uuid': '',
            'nas_name': 'test2',
            'cmp_schedule': [
                {
                    'sched_every': 1,
                    'sched_time': ['01:59', ],
                    'sched_day': [2, ],
                }],
            'cmp_file_check': 0,
            'cmp_switch': 0,
        }
        nAS = NAS(a)
        r = nAS.createNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'createNAS', body)

    def testDescribeNASGroup(self):
        a = Auth(username, pwd)
        body = {
            'group_uuid': '11111111-1111-1111-1111-111111111111',
        }
        group_uuid = '11111111-1111-1111-1111-111111111111'
        nAS = NAS(a)
        r = nAS.describeNASGroup(body, group_uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'describeNASGroup', body)

    def testModifyNAS(self):
        a = Auth(username, pwd)
        body = {
            'group_uuid': '11111111-1111-1111-1111-111111111111',
            'compress': '',
            'secret_key': '',
            'wk_list': [
                {
                    'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                    'wk_path': 'E:\\nas\\',
                }
            ],
            'nas_type': '0',
            'sync_path': '',
            'encrypt_switch': '1',
            'band_width': '',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'bk_path': 'E:\\t\\',
            'sync_uuid': '',
            'nas_name': 'test2',
            'cmp_schedule': [
                {
                    'sched_every': 1,
                    'sched_time': ['01:59', ],
                    'sched_day': [2, ],
                }],
            'cmp_file_check': 0,
            'cmp_switch': 0,
        }
        group_uuid = '11111111-1111-1111-1111-111111111111'
        nAS = NAS(a)
        r = nAS.modifyNAS(body, group_uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'modifyNAS', body)

    def testListNAS(self):
        a = Auth(username, pwd)
        body = {
            'limit': 10,
            'page': 1,
        }
        nAS = NAS(a)
        r = nAS.listNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'listNAS', body)

    def testListNASStatus(self):
        a = Auth(username, pwd)
        body = {
            'nas_uuids': [ '11111111-1111-1111-1111-111111111111'],
        }
        nAS = NAS(a)
        r = nAS.listNASStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'listNASStatus', body)

    def testStartNAS(self):
        a = Auth(username, pwd)
        body = {
            'nas_uuids': ['11111111-1111-1111-1111-111111111111'],
            'operate': 'start',
        }
        nAS = NAS(a)
        r = nAS.startNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'startNAS', body)

    def testStopNAS(self):
        a = Auth(username, pwd)
        body = {
            'nas_uuids': ['11111111-1111-1111-1111-111111111111'],
            'operate': 'stop',
        }
        nAS = NAS(a)
        r = nAS.stopNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'stopNAS', body)

    def testDeleteNAS(self):
        a = Auth(username, pwd)
        body = {
            'nas_uuids': ['11111111-1111-1111-1111-111111111111'],
        }
        nAS = NAS(a)
        r = nAS.deleteNAS(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'NAS', 'deleteNAS', body)


if __name__ == '__main__':
    unittest.main()  
