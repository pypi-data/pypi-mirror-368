
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft.active.v20200720.Sqlserver import Sqlserver
# from info2soft.active.v20200722.Sqlserver import Sqlserver
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
    
                
class SqlserverTestCase(unittest.TestCase):

    def testCreateRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'test',
            'src_db_uuid': '7B1BE386-4CB1-86AA-D39D-B644C2EADD57',
            'tgt_db_uuid': 'CD52E44B-D25A-4CE3-126F-6F5A460731E4',
            'tgt_type': 'sqlserver',
            'map_type': 'table',
            'config': {
            'start_rule_now': 1,
            'table_map': [{
            'src_user': '1',
            'src_table': '2',
            'dst_user': '1',
            'dst_table': '2',
            'column': [],},],
            'enable_cdc': 0,
            'mirror_db_uuid': '',
            'sync_mode': 1,
            'dump_thd': 1,
            'drop_old_tab': 1,},
            '_': '95f4e88ab554',
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.createRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'createRule', body)

    def testDescribeSyncRulesDML(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': '10',
            'usr': '',
            'rule_uuid': 'cF71eAdF-cEe6-bF6d-D0b8-b2675e557eA6',
            'sort_order': 'asc',
            'search': '',
            'sort': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeSyncRulesDML(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeSyncRulesDML', body)

    def testDescribeSyncRulesObjInfo(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': 'f9d7DAfA-3d5d-c501-111F-3d189ADeA1cA',
            'usr': '',
            'sort': '',
            'sort_order': '',
            'search': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeSyncRulesObjInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeSyncRulesObjInfo', body)

    def testBatchCreateRule(self):
        a = Auth(username, pwd)
        body = {
            'tgt_type': 'sqlserver',
            'map_type': 'db',
            'config': {
            'enable_cdc': 0,
            'start_rule_now': 1,
            'dump_thd': 1,
            'sync_mode': 1,
            'drop_old_tab': 1,
            'table_map': '',},
            'rule_list': [{
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'mirror_db_uuid': '',},],
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.batchCreateRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'batchCreateRule', body)

    def testModifyRule(self):
        a = Auth(username, pwd)
        body = {
            'table_map': [{
            'src_user': '1',
            'src_table': '2',
            'dst_user': '1',
            'dst_table': '2',
            'column': [],},],
            'rule_name': 'test',
            'src_db_uuid': '7B1BE386-4CB1-86AA-D39D-B644C2EADD57',
            'tgt_db_uuid': 'CD52E44B-D25A-4CE3-126F-6F5A460731E4',
            'tgt_type': 'sqlserver',
            'map_type': 'table',
            'config': {},
            'start_rule_now': 1,
            'enable_cdc': 0,
            'mirror_db_uuid': '',
            'sync_mode': 1,
            'dump_thd': 1,
            'drop_old_tab': 1,
            '_': '95f4e88ab554',
            'uuid': '',
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.modifyRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'modifyRule', body)

    def testDeleteRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.deleteRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'deleteRule', body)

    def testStartRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.startRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'startRule', body)

    def testStopRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.stopRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'stopRule', body)

    def testResumeRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.resumeRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'resumeRule', body)

    def testStopScheduleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.stopScheduleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'stopScheduleRule', body)

    def testStartScheduleRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.startScheduleRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'startScheduleRule', body)

    def testListRuleStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.listRuleStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listRuleStatus', body)

    def testCheckName(self):
        a = Auth(username, pwd)
        body = {
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.checkName(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'checkName', body)

    def testListRule(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'group_uuid': '',
            'where_args': {
            'rule_uuid': '',},
        }
        
        sqlserver = Sqlserver(a)
        r = sqlserver.listRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listRule', body)

    def testDescribeListRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '6FBC9EB9-A10A-E226-9F2B-A77B3CF1D337',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        sqlserver = Sqlserver(a)
        r = sqlserver.describeListRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeListRule', body)

    def testCreateTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_name': 'ctt->ctt',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cmp_type': 'user,table,db',
            'db_user_map': '{"CTT":"CTT"}',
            'filter_table': '[用户.表名]',
            'db_tb_map': '表映射',
            'dump_thd': 1,
            'rule_uuid': 'CFd25fA3-b4F1-68Cd-cc63-71A32DF58255',
            'polices': '"0|00:00',
            'policy_type': 'one_time',
            'concurrent_table': [
            'hh.ww',],
            'try_split_part_table': 0,
            'one_time': '2019-05-27 16:07:08',
            'repair': 0,
            'fix_related': 0,
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.createTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'createTbCmp', body)

    def testListRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '1976-12-26',
            'date_end': '1979-07-08',
            'type': -1,
            'module_type': -1,
            'query_type': 1,
            'rule_uuid': 'F530FB0E-0208-9071-66D3-E595AE7D5A4C',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.listRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listRuleLog', body)

    def testDescribeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '9bbC4b9D-9cCb-1461-edaD-BA16B1ABEff2',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        sqlserver = Sqlserver(a)
        r = sqlserver.describeTbCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeTbCmp', body)

    def testDeleteTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'force': '',
            'uuids': 'FFfEFEb1-B1Ea-5Ad8-316A-8dCE24768A13'
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.deleteTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'deleteTbCmp', body)

    def testDescribeSyncRulesFailObj(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'rule_uuid': 'c0648DC8-e7FF-3E44-4cE4-eCC8beb92F9D',
            'search': '',
            'type': 1,
            'stage': 1,
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeSyncRulesFailObj(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeSyncRulesFailObj', body)

    def testListTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.listTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listTbCmp', body)

    def testListTbCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': 'c7E49666-E6C8-4C30-48C3-3f3EA6F2AbDB',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.listTbCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listTbCmpStatus', body)

    def testListTbCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.listTbCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'listTbCmpResultTimeList', body)

    def testStopTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'tb_cmp_uuids': '4FE3d4e6-5b7E-9ACF-2F3D-2e791cf7eD53',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.stopTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'stopTbCmp', body)

    def testRestartTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'tb_cmp_uuids': '4FE3d4e6-5b7E-9ACF-2F3D-2e791cf7eD53',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.restartTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'restartTbCmp', body)

    def testDescribeTbCmpResuluTimeList(self):
        a = Auth(username, pwd)
        body = {
            'time_list': 'b165Ec3d-9Ffd-4eB2-f7bE-9Fc2DEAD5c11',
            'uuid': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeTbCmpResuluTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeTbCmpResuluTimeList', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'DD8eB893-41E1-bC49-5eD4-8f63fB6cC19D',
            'start_time': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeTbCmpResult', body)

    def testDescribeTbCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': '91Fdad26-4efC-F1CA-13c8-fb82eeFf42cE',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeTbCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeTbCmpErrorMsg', body)

    def testDescribeTbCmpCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        sqlserver = Sqlserver(a)
        r = sqlserver.describeTbCmpCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Sqlserver', 'describeTbCmpCmpResult', body)


if __name__ == '__main__':
    unittest.main()
