
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.tools.v20220622.Diagnose import Diagnose
from info2soft import Auth
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
        diagnose = Diagnose(a)
        body = {}
        r = diagnose.createDiagnose(body)
        print(r[0])

    def testDeleteDiagnose(self):
        a = Auth(username, pwd)
        diagnose = Diagnose(a)
        body = {}
        r = diagnose.deleteDiagnose(body)
        print(r[0])

    def testListDiagnose(self):
        a = Auth(username, pwd)
        diagnose = Diagnose(a)
        body = {}
        r = diagnose.listDiagnose(body)
        print(r[0])

    def testDownloadDiagnoseResult(self):
        a = Auth(username, pwd)
        diagnose = Diagnose(a)
        body = {}
        r = diagnose.downloadDiagnoseResult(body)
        print(r[0])


if __name__ == '__main__':
    unittest.main()  
