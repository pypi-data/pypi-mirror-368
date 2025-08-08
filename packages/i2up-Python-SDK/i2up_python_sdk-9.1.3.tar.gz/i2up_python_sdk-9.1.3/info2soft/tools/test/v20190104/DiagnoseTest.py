
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.tools.v20181227.Diagnose import Diagnose
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
    
                
class DiagnoseTestCase(unittest.TestCase):

    def testCreateDiagnose(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '',
            'check_type': 1,
            'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'rep_uuid': '',
        }
        diagnose = Diagnose(a)
        r = diagnose.createDiagnose(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Diagnose', 'createDiagnose', body)

    def testListDiagnose(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }
        diagnose = Diagnose(a)
        r = diagnose.listDiagnose(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Diagnose', 'listDiagnose', body)

    def testDeleteDiagnose(self):
        a = Auth(username, pwd)
        body = {
            'check_uuids': ['11111111-1111-1111-1111-111111111111'],
        }
        diagnose = Diagnose(a)
        r = diagnose.deleteDiagnose(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Diagnose', 'deleteDiagnose', body)


if __name__ == '__main__':
    unittest.main()  
