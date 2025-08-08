
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20220622.DtoLifeManagement import DtoLifeManagement
# from info2soft.resource.v20200722.DtoLifeManagement import DtoLifeManagement
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


class DtoLifeManagementTestCase(unittest.TestCase):

    def testCreateDtoLm(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'status': 0,
            'type': 1,
            'prefix': '',
            'lfa_stor': {
            'config_sw': 1,
            'days': 1,},
            'arch_stor': {
            'config_sw': 1,
            'days': 1,},
            'expr_del': {
            'config_sw': 1,
            'days': 1,},
            'sto_uuid': '',
            'host_uuid': '',
            'path': '',
            'rule_id': '',
        }
        
        dtoLifeManagement = DtoLifeManagement(a)
        r = dtoLifeManagement.createDtoLm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoLifeManagement', 'createDtoLm', body)

    def testModifyDtoLm(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'status': 0,
            'type': 1,
            'prefix': '',
            'lfa_stor': {
            'config_sw': '',
            'days': '',},
            'arch_stor': {
            'config_sw': '',
            'days': '',},
            'expr_del': {
            'config_sw': '',
            'days': '',},
            'sto_uuid': '',
            'host_uuid': '',
            'path': '',
        }
        
        dtoLifeManagement = DtoLifeManagement(a)
        r = dtoLifeManagement.modifyDtoLm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoLifeManagement', 'modifyDtoLm', body)

    def testStartDtoLm(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
            'sto_uuid': '',
            'host_uuid': '',
            'path': '',
            'rule_names': [],
        }
        
        dtoLifeManagement = DtoLifeManagement(a)
        r = dtoLifeManagement.startDtoLm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoLifeManagement', 'startDtoLm', body)

    def testStopDtoLm(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
            'sto_uuid': '',
            'host_uuid': '',
            'path': '',
            'rule_names': [],
        }

        dtoLifeManagement = DtoLifeManagement(a)
        r = dtoLifeManagement.stopDtoLm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoLifeManagement', 'stopDtoLm', body)

    def testDeleteDtoLm(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
            'sto_uuid': '',
            'host_uuid': '',
            'path': '',
            'rule_names': [],
        }

        dtoLifeManagement = DtoLifeManagement(a)
        r = dtoLifeManagement.deleteDtoLm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DtoLifeManagement', 'deleteDtoLm', body)


if __name__ == '__main__':
    unittest.main()
