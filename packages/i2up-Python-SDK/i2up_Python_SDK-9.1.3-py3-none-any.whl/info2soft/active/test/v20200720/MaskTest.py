# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft import Mask
# from info2soft.active.v20200722.Mask import Mask
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


class MaskTestCase(unittest.TestCase):

    def testListTypes(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
        }

        mask = Mask(a)
        r = mask.listTypes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listTypes', body)

    def testModifySensType(self):
        a = Auth(username, pwd)
        body = {
            'algo_name': '屏蔽姓名',
            'algo_desc': '屏蔽姓名中的名字',
            'algo_params': [
                {
                    'name': '偏移量',
                    'key': 'off',
                    'value': '1',
                    'setted': 1,
                    'type': 'int',
                },
                {
                    'name': '长度',
                    'key': 'len',
                    'value': '0',
                    'setted': 1,
                    'type': 'int',
                },
                {
                    'name': '屏蔽字符',
                    'key': 'val',
                    'value': '*',
                    'setted': 0,
                    'type': 'string',
                },
            ],
            'username': '',
            'user_uuid': '00000000-0000-0000-0000-000000000000',
            'id': 1,
            'type_name': '姓名',
            'description': '由姓氏与名字组成，用于识别某一个人。',
            'sort': 0,
            'create_time': '0',
            'params': '',
            'parent_id': 1,
            'default_algo': 1301,
            'default_algo_params': [
                {
                    'name': '偏移量',
                    'key': 'off',
                    'value': '1',
                    'setted': 1,
                    'type': 'int',
                },
                {
                    'name': '长度',
                    'key': 'len',
                    'value': '0',
                    'setted': 2,
                    'type': 'int',
                },
                {
                    'name': '屏蔽字符',
                    'key': 'val',
                    'value': '*',
                    'setted': 3,
                    'type': 'string',
                },
            ],
            '_': '704098f4051d7',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.modifySensType(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'modifySensType', body)

    def testDescriptSensType(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.descriptSensType(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'descriptSensType', body)

    def testCreateAlgo(self):
        a = Auth(username, pwd)
        body = {
            'ava_sens_type': 1,
            'parent_id': 1,
            'algo_name': '',
            'description': '',
            'params': '',
            'sort': '',
        }

        mask = Mask(a)
        r = mask.createAlgo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'createAlgo', body)

    def testListAlgos(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
        }

        mask = Mask(a)
        r = mask.listAlgos(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listAlgos', body)

    def testDescriptAlgo(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.descriptAlgo(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'descriptAlgo', body)

    def testListMaskRules(self):
        a = Auth(username, pwd)
        body = {
            'limit': 10,
            'page': 0,
        }

        mask = Mask(a)
        r = mask.listMaskRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listMaskRules', body)

    def testCreateMaskRules(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'strate': [{
                'sens_map_id': 1,
                'mask_algo_id': 1, }, ],
            'load_thread': 8,
            'compress_level': 2,
        }

        mask = Mask(a)
        r = mask.createMaskRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'createMaskRules', body)

    def testStartMaskRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        mask = Mask(a)
        r = mask.startMaskRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'startMaskRule', body)

    def testStopMaskRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': '',
        }

        mask = Mask(a)
        r = mask.stopMaskRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'stopMaskRule', body)

    def testDeleteMaskRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }

        mask = Mask(a)
        r = mask.deleteMaskRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'deleteMaskRule', body)

    def testDescribeMaskRule(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.describeMaskRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'describeMaskRule', body)

    def testListMaskRuleStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        mask = Mask(a)
        r = mask.listMaskRuleStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listMaskRuleStatus', body)

    def testListMap(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
        }

        mask = Mask(a)
        r = mask.listMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listMap', body)

    def testCreateMap(self):
        a = Auth(username, pwd)
        body = {
            'map_name': '',
            'sens_type_id': '',
            'sens_column': [{
                'user': 'I2MASK',
                'table': 'MP',
                'column': 'MP', }, ],
        }

        mask = Mask(a)
        r = mask.createMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'createMap', body)

    def testModifyMap(self):
        a = Auth(username, pwd)
        body = {
            'map_name': '',
            'sens_type_id': '',
            'sens_column': [{
                'user': 'I2MASK',
                'table': 'MP',
                'column': 'MP', }, ],
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.modifyMap(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'modifyMap', body)

    def testDeleteMap(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        mask = Mask(a)
        r = mask.deleteMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'deleteMap', body)

    def testDescriptMap(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.descriptMap(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'descriptMap', body)

    def testCreateDbMap(self):
        a = Auth(username, pwd)
        body = {
            'db_uuid': '',
            'map_name': '',
        }

        mask = Mask(a)
        r = mask.createDbMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'createDbMap', body)

    def testListDbMap(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
        }

        mask = Mask(a)
        r = mask.listDbMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listDbMap', body)

    def testDeleteDbMap(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        mask = Mask(a)
        r = mask.deleteDbMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'deleteDbMap', body)

    def testModifyDbMap(self):
        a = Auth(username, pwd)
        body = {
        }

        mask = Mask(a)
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        r = mask.modifyDbMap(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'modifyDbMap', body)

    def testCreateSensCheck(self):
        a = Auth(username, pwd)
        body = {
            'task_name': '',
            'src_db_uuid': '',
            'users': '',
            'tabs': '',
            'row': '',
            'min': '',
            'types': [{
                'type_id': 1,
                'type_arg': '', }, ],
        }

        mask = Mask(a)
        r = mask.createSensCheck(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'createSensCheck', body)

    def testModifySensCheck(self):
        a = Auth(username, pwd)
        body = {
            'task_name': '',
            'src_db_uuid': '',
            'users': '',
            'tabs': '',
            'row': '',
            'min': '',
            'types': [{
                'type_id': 1,
                'type_arg': '', }, ],
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.modifySensCheck(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'modifySensCheck', body)

    def testDeleteSensCheck(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }

        mask = Mask(a)
        r = mask.deleteSensCheck(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'deleteSensCheck', body)

    def testListSensCheck(self):
        a = Auth(username, pwd)
        body = {
            'page': 0,
            'limit': 10,
        }

        mask = Mask(a)
        r = mask.listSensCheck(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSensCheck', body)

    def testDescriptSensCheck(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.descriptSensCheck(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'descriptSensCheck', body)

    def testListSensCheckStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }

        mask = Mask(a)
        r = mask.listSensCheckStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSensCheckStatus', body)

    def testListSensCheckResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'type': '',
            'user': '',
            'table': '',
            'limit': 1,
            'page': 1,
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.listSensCheckResult(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSensCheckResult', body)

    def testListSensCheckIgnoreCol(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'col': '',
        }

        mask = Mask(a)
        r = mask.listSensCheckIgnoreCol(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSensCheckIgnoreCol', body)

    def testAlgoTest(self):
        a = Auth(username, pwd)
        body = {
            'example': {
                'orig': '1231',
                'mask': '-', },
            'parent_id': 308,
            'ava_sens_type': 8,
            'type_arg': '',
            'id': 308,
            'params': [],
            '_': '713d0acaa3283',
        }

        mask = Mask(a)
        r = mask.algoTest(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'algoTest', body)

    def testModifyMaskRules(self):
        a = Auth(username, pwd)
        body = {
            'username': 'admin',
            'user_uuid': '1BCFCAA3-E3C8-3E28-BDC5-BE36FDC2B5DC',
            'rule_uuid': 'BFD56508-9FCB-1FFF-749B-FCA2E78B4CD6',
            'src_db_uuid': '38F1AD45-5F72-2E51-DC01-0593A14A8D17',
            'tgt_db_uuid': '32C50055-A267-1E9E-65EE-FC6AAB75D390',
            'rule_type': 1,
            'rule_name': '123123',
            'node_uuid': 'A6ABF8BC-38AF-41FE-ACF7-DD9F28B0FA3F',
            'tgt_type': 'oracle',
            'db_user_map': '',
            'row_map_mode': '',
            'map_type': 'db',
            'table_map': '',
            'dbmap_topic': '',
            'sync_mode': '1',
            'start_scn': '',
            'storage_settings': '',
            'table_space_map': {
                'tgt_table_space': '',
                'table_mapping_way': 'ptop',
                'table_path_map': [],
                'table_space_name': [], },
            'other_settings': {
                'src_type': 'oracle',
                'tgt_type': 'oracle',
                'src_path': '/var/i2data/cache/',
                'file_names': [],
                'size': 1024,
                'tgt_path': '/var/i2data/cache/',
                'compress_level': 0,
                'policy': {
                    'policy_type': 'immediate',
                    'one_time': '',
                    'time_policy': '', }, },
            'error_handling': '',
            'bw_settings': '',
            'strate': [{
                'type_id': 1,
                'type_arg': '',
                'algo_pid': 4,
                'algo_id': 1301,
                'sens_column': [{
                    'user': '123',
                    'table': '123',
                    'column': '123', }, ],
                'algo_arg': [{
                    'name': '偏移量',
                    'key': 'off',
                    'value': '1',
                    'setted': 1,
                    'type': 'int', }, {
                    'name': '长度',
                    'key': 'len',
                    'value': '0',
                    'setted': 2,
                    'type': 'int', }, {
                    'name': '屏蔽字符',
                    'key': 'val',
                    'value': '*',
                    'setted': 3,
                    'type': 'string', }, ],
                'sens_map_id': '1',
                'algo_name': '屏蔽姓名',
                'sens_type_name': '姓名', }, {
                'type_id': 2,
                'type_arg': '',
                'algo_pid': 4,
                'algo_id': 1302,
                'sens_column': [{
                    'user': '123',
                    'table': '123',
                    'column': '123', }, ],
                'algo_arg': [{
                    'name': '偏移量',
                    'key': 'off',
                    'value': '1',
                    'setted': 4,
                    'type': 'int', }, {
                    'name': '长度',
                    'key': 'len',
                    'value': '0',
                    'setted': 5,
                    'type': 'int', }, {
                    'name': '屏蔽字符',
                    'key': 'val',
                    'value': '*',
                    'setted': 6,
                    'type': 'string', }, ],
                'sens_map_id': '2',
                'algo_name': '屏蔽身份证出生月日',
                'sens_type_name': '身份证号', }, ],
            'full_sync_settings': {
                'his_thread': 1, },
            'full_sync_obj_filter': [
                'INDEX',
                'VIEW',
                'FUNCTION',
                'PROCEDURE',
                'PACKAGE',
                'PACKAGE BODY',
                'SYNONYM',
                'TRIGGER',
                'SEQUENCE',
                'JAVA CLASS',
                'TYPE',
                'TYPE BODY',
                'MATERIALIZED VIEW',
                'OLD JOB',
                'JOB',
                'PRIVS',
                'CONSTRAINT',
                'JAVA RESOURCE',
                'JAVA SOURCE', ],
            'inc_sync_ddl_filter': '',
            'filter_table_settings': '',
            'etl_settings': '',
            'create_time': 1601345043,
            'start_rule_now': 1,
            'db_map_uuid': '71D59BCE-17F3-ED0D-BC76-132833F72498',
            'dml_track': '',
            'kafka_time_out': '12000',
            'part_load_balance': 'by_key',
            'kafka_message_encoding': 'UTF-8',
            'kafka': '',
            'biz_grp_list': [],
            'biz_grp_name': [],
            'modify': 1,
            '_': '4d058aa7a4ce1',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mask = Mask(a)
        r = mask.modifyMaskRules(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'modifyMaskRules', body)

    def testListSummary(self):
        a = Auth(username, pwd)
        body = {
        }

        mask = Mask(a)
        r = mask.listSummary(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSummary', body)

    def testListSummaryView(self):
        a = Auth(username, pwd)
        body = {
            'src': '',
            'dst': '',
            'status': '',
            'type': '',
            'ip': '',
        }

        mask = Mask(a)
        r = mask.listSummaryView(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mask', 'listSummaryView', body)


if __name__ == '__main__':
    unittest.main()
