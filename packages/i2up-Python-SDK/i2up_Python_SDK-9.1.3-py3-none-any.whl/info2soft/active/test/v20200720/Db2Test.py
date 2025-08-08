# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.active.v20200720.Db2 import Db2
# from info2soft.active.v20200722.Db2 import Db2
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


class Db2TestCase(unittest.TestCase):

    def testListDbRule(self):
        a = Auth(username, pwd)
        body = {
        }

        db2 = Db2(a)
        r = db2.listDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listDbRule', body)

    def testCreateDbRule(self):
        a = Auth(username, pwd)
        body = {
                   'start_rule_now': 1,
                   'rule_name': '12321',
                   'src_db_uuid': '2C4C2E77-774D-C604-9A32-5038D8E590C4',
                   'tgt_type': 'db2',
                   'tgt_db_uuid': '953C47CB-3F6C-E72F-DF1C-31522468A566',
                   'map_type': 'db',
                   'db_user_map': '',
                   'table_map': '',
                   'dbmap_topic': '',
                   'row_map_mode': 'rowid',
                   'sync_mode': 1,
                   'start_scn': '',
                   'kafka_time_out': '120000',
                   'part_load_balance': 'by_table',
                   'kafka_message_encoding': 'UTF-8',
                   'kafka': {
                       'binary_code': 'hex', },
                   'dml_track': {
                       'enable': 0,
                       'urp': 0,
                       'drp': 0,
                       'tmcol': '',
                       'delcol': '', },
                   'storage_settings': {
                       'src_max_mem': '512',
                       'src_max_disk': '5000',
                       'txn_max_mem': '10000',
                       'tf_max_size': '100',
                       'max_ld_mem': '512',
                       'tgt_extern_table': '', },
                   'other_settings': {
                       'keep_dyn_data': 0,
                       'dyn_thread': 1,
                       'dly_constraint_load': 0,
                       'zip_level': 0,
                       'ddl_cv': 0,
                       'keep_bad_act': 0,
                       'fill_lob_column': 0,
                       'keep_seq_sync': 0,
                       'keep_usr_pwd': 0,
                       'convert_urp_of_key': 0,
                       'ignore_foreign_key': 0,
                       'gen_txn': 0,
                       'run_time': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',
                       'jointing': {
                           'table': '',
                           'op': 'append',
                           'content': '', }, },
                   'error_handling': {
                       'irp': 'irpafterdel',
                       'urp': 'toirp',
                       'drp': 'ignore',
                       'load_err_set': 'continue',
                       'report_failed_dml': 0, },
                   'bw_settings': {
                       'bw_limit': '', },
                   'table_space_map': {
                       'tgt_table_space': '',
                       'table_mapping_way': 'ptop',
                       'table_path_map': [],
                       'table_space_name': [], },
                   'full_sync_settings': {
                       'load_mode': 'direct',
                       'ld_dir_opt': 0,
                       'dump_thd': 1,
                       'load_thd': 1,
                       'try_split_part_table': 1,
                       'clean_user_before_dump': 0,
                       'existing_table': 'drop_to_recycle',
                       'concurrent_table': '[]', },
                   'full_sync_obj_filter': {
                       'full_sync_obj_data': [], },
                   'inc_sync_ddl_filter': {
                       'inc_sync_ddl_data': [
                           'ALTER TABLE CHECKED',
                           'ALTER TABLE REORG',
                           'ALTER TABLE ATTACH PARTITION',
                           'CREATE INDEX NOT PART',
                           'DROP INDEX NOT PART', ], },
                   'filter_table_settings': {
                       'exclude_table': '[]', },
                   'etl_settings': {
                       'etl_table': [], },
                   'save_json_text': '',
        }

        db2 = Db2(a)
        r = db2.createDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'createDbRule', body)

    def testModifyDbRule(self):
        a = Auth(username, pwd)
        body = {
        }

        db2 = Db2(a)
        r = db2.modifyDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'modifyDbRule', body)

    def testDescribeDbRule(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        db2 = Db2(a)
        r = db2.describeDbRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'describeDbRule', body)

    def testDeleteDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.deleteDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'deleteDbRule', body)

    def testStopDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.stopDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'stopDbRule', body)

    def testResumeDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.resumeDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'resumeDbRule', body)

    def testRestartDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.restartDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'restartDbRule', body)

    def testStartAnalysisDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.startAnalysisDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'startAnalysisDbRule', body)

    def testStopAnalysisDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.stopAnalysisDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'stopAnalysisDbRule', body)

    def testResetAnalysisDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.resetAnalysisDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'resetAnalysisDbRule', body)

    def testStopAndStopAnalysisDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.stopAndStopAnalysisDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'stopAndStopAnalysisDbRule', body)

    def testStopScheduleDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.stopScheduleDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'stopScheduleDbRule', body)

    def testStartScheduleDbRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        db2 = Db2(a)
        r = db2.startScheduleDbRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'startScheduleDbRule', body)

    def testListDbRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'rule_uuid': '3FCdeF6f-9CC5-B9Ee-C4F2-8e19eb118528',
        }

        db2 = Db2(a)
        r = db2.listDbRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listDbRuleLog', body)

    def testCreateDb2Cmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_name': 'ctt->ctt',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cmp_type': 'table, database, all',
            'db_user_map': {
                'CTT': 'CTT', },
            'filter_table': '["用户.表名"]',
            'db_tb_map': '表映射',
            'dump_thd': 1,
            'rule_uuid': 'd7bed65D-4B9b-C1a2-eEfe-9Ce8BDfb8e48',
            'polices': '"0|00:00',
            'policy_type': 'one_time',
            'try_split_part_table': 0,
            'one_time': '',
            'concurrent_table': [],
            'repair': 1,
            'fix_related': 1,
        }

        db2 = Db2(a)
        r = db2.createDb2Cmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'createDb2Cmp', body)

    def testDescribeDb2Cmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        db2 = Db2(a)
        r = db2.describeDb2Cmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'describeDb2Cmp', body)

    def testDeleteDb2Rules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '7eCFCA3d-ebc2-DbB2-6DAb-BA0AE4BcDFD1',
        }

        db2 = Db2(a)
        r = db2.deleteDb2Rules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'deleteDb2Rules', body)

    def testListDb2Cmps(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }

        db2 = Db2(a)
        r = db2.listDb2Cmps(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listDb2Cmps', body)

    def testListDb2CmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }

        db2 = Db2(a)
        r = db2.listDb2CmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listDb2CmpStatus', body)

    def testCmpStopDb2Cmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '6ef11d7e-2791-4ddC-A39D-fCFbeC53f72A',
            'operate': '',
        }

        db2 = Db2(a)
        r = db2.cmpStopDb2Cmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'cmpStopDb2Cmp', body)

    def testCmpRestartDb2Cmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': '6ef11d7e-2791-4ddC-A39D-fCFbeC53f72A',
            'operate': '',
        }

        db2 = Db2(a)
        r = db2.cmpRestartDb2Cmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'cmpRestartDb2Cmp', body)

    def testDeleteCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'time_list': 'DAfbCAeA-aE6e-cF7b-9bc5-9d5b0C6Fbf7E',
            'uuid': '',
        }

        db2 = Db2(a)
        r = db2.deleteCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'deleteCmpResult', body)

    def testListCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'limit': '',
            'offset': '',
            'uuid': '',
        }

        db2 = Db2(a)
        r = db2.listCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listCmpResult', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'DecFc58D-BAf2-83CD-641D-a1dEE29BF875',
            'start_time': '',
        }

        db2 = Db2(a)
        r = db2.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'describeTbCmpResult', body)

    def testlistDb2ResultFix(self):
        a = Auth(username, pwd)
        body = {
            'time_list': 'FD9bC2d9-7E7A-3389-fEeC-Ac4d475ddDE9',
            'uuid': 'bfE3fF9C-ef78-cF26-63C2-EEFc2Fd6bddc',
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'start_time': '',
        }

        db2 = Db2(a)
        r = db2.listDb2ResultFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listDb2ResultFix', body)

    def testDescribeCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'ADeEf4b3-E5da-82DF-FCFF-fCe76EE288D6',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }

        db2 = Db2(a)
        r = db2.describeCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'describeCmpErrorMsg', body)

    def testListFixResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        db2 = Db2(a)
        r = db2.listFixResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listFixResult', body)

    def testExportCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        db2 = Db2(a)
        r = db2.exportCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'exportCmpResult', body)

    def testListCmpDiffMap(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'time': '',
        }

        db2 = Db2(a)
        r = db2.listCmpDiffMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Db2', 'listCmpDiffMap', body)


if __name__ == '__main__':
    unittest.main()
