
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.fsp.FspMove import FspMove
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
    

class FspMoveTestCase(unittest.TestCase):

    def testListFspMoveNic(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
        }
        fspMove = FspMove(a)
        r = fspMove.listFspMoveNic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'listFspMoveNic', body)

    def testListFspMoveDir(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuid': '',
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
        }
        fspMove = FspMove(a)
        r = fspMove.listFspMoveDir(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'listFspMoveDir', body)

    def testVerifyFspMoveLicense(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
            'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
        }
        fspMove = FspMove(a)
        r = fspMove.verifyFspMoveLicense(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'verifyFspMoveLicense', body)

    def testVerifyFspMoveOldRule(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
            'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
        }
        fspMove = FspMove(a)
        r = fspMove.verifyFspMoveOldRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'verifyFspMoveOldRule', body)

    def testVerifyFspMoveVolumeSpace(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
            'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
            'sync_item': '/',
        }
        fspMove = FspMove(a)
        r = fspMove.verifyFspMoveVolumeSpace(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'verifyFspMoveVolumeSpace', body)

    def testVerifyFspMoveOsVersion(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
            'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
        }
        fspMove = FspMove(a)
        r = fspMove.verifyFspMoveOsVersion(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'verifyFspMoveOsVersion', body)

    def testVerifyFspMoveEnvironment(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '',
            'bk_uuid': '',
            'wk_path': [{
            '': ''}],
            'bk_path': [{
            '': ''}],
        }

        fspMove = FspMove(a)
        r = fspMove.verifyFspMoveEnvironment(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'fspMove', 'verifyFspMoveEnvironment', body)

    def testCreateFspMove(self):
        a = Auth(username, pwd)
        body = {
            'fsp_move': {
                'fsp_name': 'linuxMove',
                'service_uuid': '',
                'monitor_type': 0,
                'bk_path': [
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
                'compress': '0',
                'net_mapping': [],
                'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
                'encrypt_switch': '0',
                'mirr_open_type': '0',
                'sync_item': '/',
                'mirr_sync_flag': '0',
                'net_mapping_type': '2',
                'mirr_sync_attr': '1',
                'band_width': '3*03:00-04:00*2m',
                'excl_path': [
                    '/cgroup/',
                    '/dev/',
                    '/etc/X11/xorg.conf/',
                    '/etc/init.d/i2node/',
                    '/etc/rc.d/init.d/i2node/',
                    '/etc/sdata/',
                    '/lost+found/',
                    '/media/',
                    '/mnt/',
                    '/proc/',
                    '/run/',
                    '/selinux/',
                    '/sys/',
                    '/tmp/',
                    '/usr/local/sdata/',
                    '/var/i2/',
                    '/var/i2data/',
                    '/var/lock/',
                    '/var/run/vmblock-fuse/'
                ],
                'fsp_wk_shut_flag': '2',
                'secret_key': '',
                'wk_path': [
                    '/',
                    '/bin/',
                    '/boot/',
                    '/etc/',
                    '/lib/',
                    '/lib64/',
                    '/root/',
                    '/sbin/',
                    '/usr/bin/',
                    '/usr/lib/',
                    '/usr/lib64/',
                    '/usr/libexec/',
                    '/usr/local/',
                    '/usr/sbin/',
                    '/var/lib/nfs/'
                ],
                'mirr_file_check': '0',
                'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
                'failover': '2',
                    }
        }
        fspMove = FspMove(a)
        r = fspMove.createFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'createFspMove', body)

    def testModifyFspMove(self):
        a = Auth(username, pwd)
        body = {
            'fsp_move': {
                'fsp_uuid': '3C6B932A-9140-7C37-9639-EB8F44654F18',
                'excl_path': [
                    '/cgroup/',
                    '/dev/',
                    '/etc/X11/xorg.conf/',
                    '/etc/init.d/i2node/',
                    '/etc/rc.d/init.d/i2node/',
                    '/etc/sdata/',
                    '/lost+found/',
                    '/media/',
                    '/mnt/',
                    '/proc/',
                    '/run/',
                    '/selinux/',
                    '/sys/',
                    '/tmp/',
                    '/usr/local/sdata/',
                    '/var/i2/',
                    '/var/i2data/',
                    '/var/lock/',
                    '/var/run/vmblock-fuse/'
                ],
                'random_str': '0DD4E727-70AB-62C6-BEB5-D012DFAE46E3',
                'fsp_wk_shut_flag': '2',
                'monitor_type': 0,
                'mirr_sync_attr': '1',
                'net_mapping_type': '2',
                'mirr_sync_flag': '0',
                'mirr_file_check': '0',
                'sync_item': '/',
                'secret_key': '',
                'failover': '2',
                'fsp_name': 'linuxMove',
                'mirr_open_type': '0',
                'bk_uuid': 'C11FE572-5207-3359-DB85-001E95F5F185',
                'bk_path': [
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
                'net_mapping': [],
                'service_uuid': '',
                'wk_uuid': 'CE77F3D6-A6E3-A385-CE66-712313B7DDE8',
                'compress': '0',
                'encrypt_switch': '0',
                'move_type': '0',
                'wk_path': ["/", "/bin/", "/boot/", "/etc/", "/lib/", "/lib64/", "/root/", "/sbin/", "/usr/bin/",
                            "/usr/lib/", "/usr/lib64/", "/usr/libexec/", "/usr/local/", "/usr/sbin/", "/var/lib/nfs/"],
                'band_width': '3*03:00-16:00*2m'
            }
        }
        fspMove = FspMove(a)
        r = fspMove.modifyFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'modifyFspMove', body)

    def testDescribeFspMove(self):
        a = Auth(username, pwd)
        body = {
            'fsp_move': {
                'fsp_uuid': '3C6B932A-9140-7C37-9639-EB8F44654F18'
            }
        }
        fspMove = FspMove(a)
        r = fspMove.describeFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'describeFspMove', body)

    def testDeleteFspMove(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.deleteFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'deleteFspMove', body)

    def testListFspMove(self):
        a = Auth(username, pwd)
        body = {
            'search_field': '',
            'limit': 1,
            'page': 1,
            'search_value': '',
        }
        fspMove = FspMove(a)
        r = fspMove.listFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'listFspMove', body)

    def testStartFspMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.startFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'startFspMove', body)

    def testStopFspMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.stopFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'stopFspMove', body)

    def testMoveFspMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'move',
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.moveFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'moveFspMove', body)

    def testRebootFspMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'reboot',
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.rebootFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'rebootFspMove', body)


    def testListFspMoveStatus(self):
        a = Auth(username, pwd)
        body = {
            'fsp_uuids': ['3C6B932A-9140-7C37-9639-EB8F44654F18'],
        }
        fspMove = FspMove(a)
        r = fspMove.listFspMoveStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'listFspMoveStatus', body)

    def testBatchCreateFspMove(self):
        a = Auth(username, pwd)
        body = {
            'base_info_list': {
            'service_uuid': '',
            'monitor_type': 0,
            'compress': 0,
            'net_mapping': [{
            'bk_nic': {
            'name': 'Ethernet0',
            'type': '0',
            'ip': '192.168.72.74/255.255.240.0',},
            'wk_nic': {
            'name': 'Ethernet0',
            'type': '0',
            'ip': '192.168.72.73/255.255.240.0'}}],
            'encrypt_switch': 0,
            'mirr_open_type': '0',
            'mirr_sync_flag': '0',
            'net_mapping_type': '2',
            'mirr_sync_attr': '1',
            'band_width': '',
            'fsp_wk_shut_flag': 2,
            'secret_key': '',
            'mirr_file_check': '0',
            'failover': 0,
            'excl_driver': [
            'inf1',
            'inf2',],
            'compress_switch': 1,
            'encrypt': 1,
            'wk_data_type': 1,
            'auto_start': 1,
            'bkup_one_time': 1,
            'backup_type': '',},
            'common_params': {
            'batch_name': '',
            'rep_prefix': '',
            'rep_sufix': '',
            'variable_type': 0},
            'node_list': [{
            'bk_uuid': '',
            'excl_path': [],
            'bk_path': [],
            'wk_uuid': '',
            'wk_path': [],
            'proxy_uuid': '',
            'data_ip_uuid': '',
            'sync_item': '/'}]
        }

        fspMove = FspMove(a)
        r = fspMove.batchCreateFspMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'batchCreateFspMove', body)

    def testListFspMoveDriverInfo(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '',
        }

        fspMove = FspMove(a)
        r = fspMove.listFspMoveDriverInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'FspMove', 'listFspMoveDriverInfo', body)


if __name__ == '__main__':
    unittest.main()  
