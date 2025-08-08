# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.active.v20220622.MongoDB import MongoDB
# from info2soft.active.v20200722.MongoDB import MongoDB
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


class MongoDBTestCase(unittest.TestCase):

    def testCreateMongoRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'tgt_type': 'sqlserver',
            'map_type': 'db',
            'config': {
                'start_rule_now': 1,
                'table_map': '',
                'full_sync': 0,
                'incre_sync': 1,
                'kafka': {
                    'binary_code': '', },
                'kafka_time_out': '',
                'part_load_balance': '',
                'kafka_message_encoding': '',
                'dbmap_topic': '',
                'db_user_map': '', },
        }

        mongoDB = MongoDB(a)
        r = mongoDB.createMongoRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'createMongoRule', body)

    def testModifyMongoRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'tgt_type': 'sqlserver',
            'map_type': 'db',
            'config': {
                'start_rule_now': 1,
                'table_map': '',
                'full_sync': 0,
                'incre_sync': 1,
                'kafka': {
                    'binary_code': '', },
                'kafka_time_out': '',
                'part_load_balance': '',
                'kafka_message_encoding': '', },
        }

        mongoDB = MongoDB(a)
        r = mongoDB.modifyMongoRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'modifyMongoRule', body)

    def testDeleteMongoRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'force': 'true',
        }

        mongoDB = MongoDB(a)
        r = mongoDB.deleteMongoRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'deleteMongoRule', body)

    def testListMongoStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        mongoDB = MongoDB(a)
        r = mongoDB.listMongoStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'listMongoStatus', body)

    def testResumeMongoRules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'operate': 'true',
        }

        mongoDB = MongoDB(a)
        r = mongoDB.resumeMongoRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'resumeMongoRules', body)

    def testStopMongoRules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'operate': 'true',
        }

        mongoDB = MongoDB(a)
        r = mongoDB.stopMongoRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'stopMongoRules', body)

    def testRestartMongoRules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'operate': 'true',
        }

        mongoDB = MongoDB(a)
        r = mongoDB.restartMongoRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'restartMongoRules', body)

    def testListMongoRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'rule_uuid': '86F1BfaA-C4b6-dFfF-4cCB-DA94ea4C2Cfd',
        }

        mongoDB = MongoDB(a)
        r = mongoDB.listMongoRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'listMongoRuleLog', body)

    def testListRule(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'group_uuid': '',
            'where_args': {
                'rule_uuid': '', },
        }

        mongoDB = MongoDB(a)
        r = mongoDB.listRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'listRule', body)

    def testDescribeListRule(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mongoDB = MongoDB(a)
        r = mongoDB.describeListRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'MongoDB', 'describeListRule', body)


if __name__ == '__main__':
    unittest.main()
