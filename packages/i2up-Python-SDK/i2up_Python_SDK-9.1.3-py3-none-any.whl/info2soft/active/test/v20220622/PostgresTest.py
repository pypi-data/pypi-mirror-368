
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.active.v20220622.Postgres import Postgres
# from info2soft.active.v20200722.Postgres import Postgres
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


class PostgresTestCase(unittest.TestCase):

    def testListPgsqlRule(self):
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
        
        postgres = Postgres(a)
        r = postgres.listPgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'listPgsqlRule', body)

    def testCreatePgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'test',
            'src_db_uuid': '7B1BE386-4CB1-86AA-D39D-B644C2EADD57',
            'tgt_db_uuid': 'CD52E44B-D25A-4CE3-126F-6F5A460731E4',
            'tgt_type': 'sqlserver',
            'map_type': 'table',
            'config': {
            'table_map': [{
            'src_user': '1',
            'src_table': '2',
            'dst_user': '1',
            'dst_table': '2',
            'column': [],},],
            'start_rule_now': 1,
            'db_user_map': '',
            'dbmap_topic': '',
            'full_sync': 1,
            'incre_sync': 1,
            'full_sync_mode': 'logic',
            'row_map_mode': 'rowid',
            'kafka_time_out': '120000',
            'part_load_balance': 'by_table',
            'kafka_message_encoding': 'UTF-8',},
        }
        
        postgres = Postgres(a)
        r = postgres.createPgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'createPgsqlRule', body)

    def testModifyPgsqlRule(self):
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
            'full_sync': 1,
            'incre_sync': 1,
            'full_sync_mode': '',
            'db_user_map': {},
            'dbmap_topic': '',
            'row_map_mode': '',
            'kafka_time_out': '',
            'part_load_balance': '',
            'kafka_message_encoding': '',},
            'rule_uuid': '',
        }
        
        postgres = Postgres(a)
        r = postgres.modifyPgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'modifyPgsqlRule', body)

    def testDeletePgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        postgres = Postgres(a)
        r = postgres.deletePgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'deletePgsqlRule', body)

    def testStopPgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        postgres = Postgres(a)
        r = postgres.stopPgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'stopPgsqlRule', body)

    def testRestartPgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        postgres = Postgres(a)
        r = postgres.restartPgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'restartPgsqlRule', body)

    def testResumePgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        postgres = Postgres(a)
        r = postgres.resumePgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'resumePgsqlRule', body)

    def testStopSchedulePgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        postgres = Postgres(a)
        r = postgres.stopSchedulePgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'stopSchedulePgsqlRule', body)

    def testStartSchedulePgsqlRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        postgres = Postgres(a)
        r = postgres.startSchedulePgsqlRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'startSchedulePgsqlRule', body)

    def testListPgsqlStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        postgres = Postgres(a)
        r = postgres.listPgsqlStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'listPgsqlStatus', body)

    def testListPgsqlRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'rule_uuid': '95efBe55-CB86-5067-c1C7-9CbCDa2Bcf35',
        }
        
        postgres = Postgres(a)
        r = postgres.listPgsqlRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'listPgsqlRuleLog', body)

    def testDescribePgsqlRules(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        postgres = Postgres(a)
        r = postgres.describePgsqlRules(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Postgres', 'describePgsqlRules', body)


if __name__ == '__main__':
    unittest.main()
