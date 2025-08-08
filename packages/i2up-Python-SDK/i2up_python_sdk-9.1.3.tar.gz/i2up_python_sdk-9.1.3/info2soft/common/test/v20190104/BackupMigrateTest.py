
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.common.BackupMigrate import BackupMigrate
# from info2soft.common.v20200722.BackupMigrate import BackupMigrate
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


class BackupMigrateTestCase(unittest.TestCase):

    def testDecribeCcMoveRemoteStatus(self):
        a = Auth(username, pwd)
        body = {
            'access_key': '',
            'secret_key': '',
            'cc_ip': '172.0.0.1:58086',
            'cc_port': '',
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.decribeCcMoveRemoteStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'decribeCcMoveRemoteStatus', body)

    def testDecribeCcMoveModules(self):
        a = Auth(username, pwd)
        body = {
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.decribeCcMoveModules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'decribeCcMoveModules', body)

    def testCreateCcMove(self):
        a = Auth(username, pwd)
        body = {
            'cc_ip': '172.0.0.1',
            'access_key': '',
            'secret_key': '',
            'module_list': [
            'cmp',
            'rep',
            'fsp',
            'dto',],
            'prefix': '',
            'suffix': '',
            'cc_port': '',
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.createCcMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'createCcMove', body)

    def testDecribeCcMoveStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.decribeCcMoveStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'decribeCcMoveStatus', body)

    def testListCcMove(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.listCcMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'listCcMove', body)

    def testDeleteCcMove(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.deleteCcMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'deleteCcMove', body)

    def testDecribeCcMoveTable(self):
        a = Auth(username, pwd)
        body = {
            'table': '',
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.decribeCcMoveTable(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'decribeCcMoveTable', body)

    def testMakeCcMoveRemigrate(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'conflict_uuid': '',
            'module': '',
            'model_name': '',
            'new_name': '',
        }
        
        backupMigrate = BackupMigrate(a)
        r = backupMigrate.makeCcMoveRemigrate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'BackupMigrate', 'makeCcMoveRemigrate', body)


if __name__ == '__main__':
    unittest.main()
