
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Credential import Credential
# from info2soft.common.v20200722.Credential import Credential
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


class CredentialTestCase(unittest.TestCase):

    def testListCredential(self):
        a = Auth(username, pwd)
        body = {
            'cred_type': 1,
        }
        
        credential = Credential(a)
        r = credential.listCredential(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'listCredential', body)

    def testCreateCredential(self):
        a = Auth(username, pwd)
        body = {
            'cred_type': 1,
            'cred_name': '',
            'os_user': '',
            'os_pwd': '',
            'description': '',
        }
        
        credential = Credential(a)
        r = credential.createCredential(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'createCredential', body)

    def testDescribeCredential(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        credential = Credential(a)
        r = credential.describeCredential(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'describeCredential', body)

    def testModifyCredential(self):
        a = Auth(username, pwd)
        body = {
            'cred_type': 1,
            'cred_name': '',
            'os_user': '',
            'os_pwd': '',
            'description': '',
            'random_str': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        credential = Credential(a)
        r = credential.modifyCredential(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'modifyCredential', body)

    def testDeleteCredential(self):
        a = Auth(username, pwd)
        body = {
            'cred_uuids': [],
        }
        
        credential = Credential(a)
        r = credential.deleteCredential(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'deleteCredential', body)

    def testDownloadTemplate(self):
        a = Auth(username, pwd)
        body = {
            'type': 'cred_csv',
        }
        
        credential = Credential(a)
        r = credential.downloadTemplate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'downloadTemplate', body)

    def testBatchImportCredential(self):
        a = Auth(username, pwd)
        body = {
        }
        
        credential = Credential(a)
        r = credential.batchImportCredential(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Credential', 'batchImportCredential', body)


if __name__ == '__main__':
    unittest.main()
