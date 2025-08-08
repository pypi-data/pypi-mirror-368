# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.ha.v20181227.AppHighAvailability import AppHighAvailability
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


class AppHighAvailabilityTestCase(unittest.TestCase):

    def testHa(self):
        a = Auth(username, pwd)
        body = {
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.ha(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'ha', body)

    def testHaVerifyName(self):
        a = Auth(username, pwd)
        body = {
            'ha_name': '',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.haVerifyName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'haVerifyName', body)

    def testDescribeVolumeInfo(self):
        a = Auth(username, pwd)
        body = {
            'master_uuid': '',
            'slave_uuid': '',
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.describeVolumeInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'describeVolumeInfo', body)

    def testListStageOptions(self):
        a = Auth(username, pwd)
        body = {
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listStageOptions(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listStageOptions', body)

    def testCreateHAGroup(self):
        a = Auth(username, pwd)
        body = {
            'group_name': '111',
            'error_confirm': 1,
            'switch_confirm': 1,
            'ha_rules': [
            'B95DB026-AEDF-737A-0442-B5134660D204',
            '128C2F7D-0795-41F3-1274-3FBAA2449BAD',
            '214E0B0C-6BFA-B1D7-1AFC-C11E3B5874C0',
            '2FD74EEE-CFDB-FB01-8E11-B6560B6D20F8',],
            'stage': {
            'step_1': {
            'ha_rule': [
            'B95DB026-AEDF-737A-0442-B5134660D204',
            '128C2F7D-0795-41F3-1274-3FBAA2449BAD',],
            'failover_serial': 1,
            'failback_serial': -1,
            'haList': [{
            'ha_name': 'tst',
            'ha_uuid': 'B95DB026-AEDF-737A-0442-B5134660D204',},{
            'ha_name': 'test4',
            'ha_uuid': '128C2F7D-0795-41F3-1274-3FBAA2449BAD',},],},
            'step_2': {
            'ha_rule': [
            '214E0B0C-6BFA-B1D7-1AFC-C11E3B5874C0',
            '2FD74EEE-CFDB-FB01-8E11-B6560B6D20F8',],
            'failover_serial': 2,
            'failback_serial': -2,
            'haList': [{
            'ha_name': 'test3',
            'ha_uuid': '214E0B0C-6BFA-B1D7-1AFC-C11E3B5874C0',
            'disabled': 1,},{
            'ha_name': 'test2',
            'ha_uuid': '2FD74EEE-CFDB-FB01-8E11-B6560B6D20F8',
            'disabled': 1,},],},},
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.createHAGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'createHAGroup', body)

    def testListHAGroup(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
            'search_field': 'group_name',
            'search_value': '',
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listHAGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listHAGroup', body)

    def testDeleteHAGroup(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'CFCEDC75-F48E-22B0-8A67-DE1FCA51C4C7',],
        }

        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.deleteHAGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'deleteHAGroup', body)

    def testModifyHAGroup(self):
        a = Auth(username, pwd)
        body = {
            'group_uuid': 'CFCEDC75-F48E-22B0-8A67-DE1FCA51C4C7',
            'group_name': '111',
            'error_confirm': 1,
            'switch_confirm': 1,
            'ha_rules': [
            'B95DB026-AEDF-737A-0442-B5134660D204',
            '128C2F7D-0795-41F3-1274-3FBAA2449BAD',],
            'stage': {
            'step_1': {
            'ha_rule': [
            'B95DB026-AEDF-737A-0442-B5134660D204',
            '128C2F7D-0795-41F3-1274-3FBAA2449BAD',],
            'failover_serial': 1,
            'failback_serial': -1,
            'haList': [{
            'ha_name': 'tst',
            'ha_uuid': 'B95DB026-AEDF-737A-0442-B5134660D204',},{
            'ha_name': 'test4',
            'ha_uuid': '128C2F7D-0795-41F3-1274-3FBAA2449BAD',},],},},
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.modifyHAGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'modifyHAGroup', body)

    def testDescribeHAGroup(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.describeHAGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'describeHAGroup', body)

    def testForceSwitchHAGroup(self):
        a = Auth(username, pwd)
        body = {
            'ha_uuids': [
            'B95DB026-AEDF-737A-0442-B5134660D204',
            '128C2F7D-0795-41F3-1274-3FBAA2449BAD',],
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.forceSwitchHAGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'forceSwitchHAGroup', body)

    def testListHASwitchTaskStatus(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': 'F696DC12-6727-B799-93D4-8B2213086F5A',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listHASwitchTaskStatus(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listHASwitchTaskStatus', body)

    def testPauseHAGroupSwitch(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'pause',
            'task_uuid': 'F696DC12-6727-B799-93D4-8B2213086F5A',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.pauseHAGroupSwitch(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'pauseHAGroupSwitch', body)


    def testResumeHAGroupSwitch(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'resume',
            'task_uuid': 'F696DC12-6727-B799-93D4-8B2213086F5A',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.resumeHAGroupSwitch(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'resumeHAGroupSwitch', body)


if __name__ == '__main__':
    unittest.main()
