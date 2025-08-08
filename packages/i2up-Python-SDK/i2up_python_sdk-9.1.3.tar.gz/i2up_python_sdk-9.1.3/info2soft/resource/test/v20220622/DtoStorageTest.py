
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.resource.v20220622.DtoStorage import DtoStorage
# from info2soft.dto.v20200722.DtoStorage import DtoStorage
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


class DtoStorageTestCase(unittest.TestCase):

    def testCreateDtoStorage(self):
        a = Auth(username, pwd)
        body = {
            'sto_name': '',
            'sto_type': 0,
            'address': '',
            'access_key': '',
            'secret_key': '',
            'part_size': 0,
            'comment': '',
            'user': '',
            'pwd': '',
            'remote_path': '',
        }
        
        dtoStorage = DtoStorage(a)
        r = dtoStorage.createDtoStorage(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'createDtoStorage', body)

    def testModifyDtoStorage(self):
        a = Auth(username, pwd)
        body = {
            'random_str': '',
            'sto_name': '',
            'access_key': '',
            'secret_key': '',
            'part_size': 0,
            'address': '',
            'user': '',
            'pwd': '',
            'comment': '',
            'remote_path': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dtoStorage = DtoStorage(a)
        r = dtoStorage.modifyDtoStorage(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'modifyDtoStorage', body)

    def testDescribeDtoStorage(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dtoStorage = DtoStorage(a)
        r = dtoStorage.describeDtoStorage(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'describeDtoStorage', body)

    def testListDtoStorage(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'search_value': '',
            'search_field': '',
            'page': 1,
        }
        
        dtoStorage = DtoStorage(a)
        r = dtoStorage.listDtoStorage(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'listDtoStorage', body)

    def testDeleteDtoStorage(self):
        a = Auth(username, pwd)
        body = {
            'sto_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        dtoStorage = DtoStorage(a)
        r = dtoStorage.deleteDtoStorage(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'deleteDtoStorage', body)

    def testModifyDtoStorageType(self):
        a = Auth(username, pwd)
        body = {
            'list': {},
            'type': '',
        }

        dtoStorage = DtoStorage(a)
        r = dtoStorage.modifyDtoStorageType(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'modifyDtoStorageType', body)

    def testListBuckets(self):
        a = Auth(username, pwd)
        body = {
            'sto_uuid': '',
        }

        dtoStorage = DtoStorage(a)
        r = dtoStorage.listBuckets(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoStorage', 'listBuckets', body)


if __name__ == '__main__':
    unittest.main()
