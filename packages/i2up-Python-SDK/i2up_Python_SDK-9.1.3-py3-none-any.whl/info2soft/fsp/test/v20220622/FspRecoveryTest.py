# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
# from info2soft.fsp.FspRecovery import FspRecovery
from info2soft.fsp.v20220622.FspRecovery import FspRecovery
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


class FspRecoveryTestCase(unittest.TestCase):

    def testListFspRecoveryDir(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'dst_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
            'fsp_uuid': '',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecoveryDir(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecoveryDir', body)

    def testListFspRecoveryPoint(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'rc_data_path': '/fsp_bk/192.168.71.77_26821/',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecoveryPoint(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecoveryPoint', body)

    def testVerifyFspRecoveryVolumeSpace(self):
        a = Auth(username, pwd)
        body = {
            'sync_item': '/',
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
            'dst_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.verifyFspRecoveryVolumeSpace(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'verifyFspRecoveryVolumeSpace', body)

    def testVerifyFspRecoveryLicense(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.verifyFspRecoveryLicense(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'verifyFspRecoveryLicense', body)

    def testVerifyFspRecoveryOldRule(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.verifyFspRecoveryOldRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'verifyFspRecoveryOldRule', body)

    def testVerifyFspRecoveryOsVersion(self):
        a = Auth(username, pwd)
        body = {
            'dst_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
            'wk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'bk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.verifyFspRecoveryOsVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'verifyFspRecoveryOsVersion', body)

    def testCreateFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_recovery': {
                'dst_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
                'monitor_type': 0,
                'encrypt_switch': '0',
                'net_mapping': [
                    {
                        'bk_nic': {
                            'type': '0',
                            'name': 'Ethernet0',
                            'ip': '192.168.72.74/255.255.240.0',
                        },
                        'wk_nic': {
                            'name': 'Ethernet0',
                            'type': '0',
                            'ip': '192.168.72.73/255.255.240.0'
                        }
                    }
                ],
                'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
                'mirr_sync_attr': '1',
                'secret_key': '',
                'bk_path': [
                    '/fsp_bk/192.168.71.77_26821/20190111113656/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/bin/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/boot/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/etc/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/lib/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/lib64/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/root/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/sbin/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/bin/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/lib/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/lib64/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/libexec/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/local/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/usr/sbin/',
                    '/fsp_bk/192.168.71.77_26821/20190111113656/var/lib/nfs/',
                ],
                'band_width': '',
                'fsp_name': 'testRC',
                'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
                'net_mapping_type': '2',
                'mirr_open_type': '0',
                'restore_point': '20190111113656',
                'mirr_file_check': '0',
                'compress': '0',
                'service_uuid': '',
                'excl_path': [],
                'wk_path': [
                    '/',
                    '/I2FFO/bin/',
                    '/I2FFO/boot/',
                    '/I2FFO/etc/',
                    '/I2FFO/lib/',
                    '/I2FFO/lib64/',
                    '/I2FFO/root/',
                    '/I2FFO/sbin/',
                    '/I2FFO/usr/bin/',
                    '/I2FFO/usr/lib/',
                    '/I2FFO/usr/lib64/',
                    '/I2FFO/usr/libexec/',
                    '/I2FFO/usr/local/',
                    '/I2FFO/usr/sbin/',
                    '/I2FFO/var/lib/nfs/'
                ],
                'mirr_sync_flag': '0',
                'fsp_wk_shut_flag': '2',
                'sync_item': '/',
                'failover': '2',
                'fsp_type': '5',
                'random_str': '11111111-1111-1111-1111-111111111111'
            }
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.createFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'createFspRecovery', body)

    def testModifyFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuid': '11111111-1111-1111-1111-111111111111',
            'fsp_recovery': {
                'restore_point': '20180724164452',
                'fsp_wk_shut_flag': '2',
                'excl_path': [],
                'secret_key': '',
                'band_width': '3*03:00-14:00*2m',
                'compress': '0',
                'wk_path': [],
                'net_mapping': [
                    {
                        'bk_nic': {
                            'type': '0',
                            'name': 'Ethernet0',
                            'ip': '192.168.72.74/255.255.240.0',
                        },
                        'wk_nic': {
                            'name': 'Ethernet0',
                            'type': '0',
                            'ip': '192.168.72.73/255.255.240.0'
                        }
                    }
                ],
                'service_uuid': '',
                'wk_uuid': '0DD4E727-70AB-62C6-BEB5-D012DFAE46E3',
                'net_mapping_type': '2',
                'bk_path': [],
                'fsp_name': 'rrrrr',
                'mirr_sync_flag': '0',
                'mirr_file_check': '0',
                'monitor_type': 0,
                'sync_item': 'C:',
                'mirr_sync_attr': '1',
                'random_str': '0DD4E727-70AB-62C6-BEB5-D012DFAE46E3',
                'dst_path': '???',
                'encrypt_switch': '0',
                'bk_uuid': '0DD4E727-70AB-62C6-BEB5-D012DFAE46E3',
                'mirr_open_type': '0',
                'failover': '2',
                'fsp_type': '',
            },
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.modifyFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'modifyFspRecovery', body)

    def testDesribeFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuid': '11111111-1111-1111-1111-111111111111'
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.desribeFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'desribeFspRecovery', body)

    def testDeleteFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.deleteFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'deleteFspRecovery', body)

    def testListFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'search_field': '',
            'page': 1,
            'limit': 10,
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecovery', body)

    def testStartFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
            'operate': 'start',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.startFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'startFspRecovery', body)

    def testStopFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
            'operate': 'stop',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.stopFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'stopFspRecovery', body)

    def testMoveFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
            'operate': 'move',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.moveFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'moveFspRecovery', body)

    def testRebootFspRecovery(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
            'operate': 'reboot',
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.rebootFspRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'rebootFspRecovery', body)

    def testListFspRecoveryStatus(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': [
               '11111111-1111-1111-1111-111111111111'
            ]
        }
        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecoveryStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecoveryStatus', body)

    def testListFspRecoveryNic(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'dst_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
            'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
        }

        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecoveryNic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecoveryNic', body)

    def testVerifyEnvironment(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'wk_uuid': '42614852-BB62-1EF7-FED0-D2354BF3149D',
            'wk_path': '/fsp_bk/192.168.71.77_26821/20190111113656/',
            'cbt_switch': 1,
            'task_type': 6
        }

        fspRecovery = FspRecovery(a)
        r = fspRecovery.verifyEnvironment(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'verifyEnvironment', body)

    def testListFspRecoveryDriverInfo(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'F85DFEC0-149E-373D-0B9E-3DA9A5C43940',
            'backup_dir': '/fsp_bk/192.168.71.77_26821/20190111113656/',
            'restore_point': '42614852-BB62-1EF7-FED0-D2354BF3149D',
        }

        fspRecovery = FspRecovery(a)
        r = fspRecovery.listFspRecoveryDriverInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspRecovery', 'listFspRecoveryDriverInfo', body)


if __name__ == '__main__':
    unittest.main()
