
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.common.Storage import Storage
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
    
                
class StorageTestCase(unittest.TestCase):

    def testListStorageInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'rep_uuid': 'F97B3FD5-4D5D-41EE-22A9-740A74E1E13C',
            'byte_format': 1,
        }
        storage = Storage(a)
        r = storage.listStorageInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Storage', 'listStorageInfo', body)


if __name__ == '__main__':
    unittest.main()  
