# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.active.v20200720.Oceanbase import Oceanbase
# from info2soft.active.v20200722.Oceanbase import Oceanbase
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


class OceanbaseTestCase(unittest.TestCase):

    def testListOceanRule(self):
        a = Auth(username, pwd)
        body = {
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.listOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'listOceanRule', body)

    def testCreateOceanRule(self):
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
                'run_time': '"12*00:00-13:00*40M,3*00:00-13:00*40M"', },
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
                'concurrent_table': '[]',
                'sync_mode': 0,
                'start_scn': '', },
            'full_sync_obj_filter': {
                'full_sync_obj_data': [], },
            'inc_sync_ddl_filter': {
                'inc_sync_ddl_data': [], },
            'filter_table_settings': {
                'exclude_table': '[]', },
            'etl_settings': {
                'etl_table': [], },
            '_': '489d781db90cb',
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.createOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'createOceanRule', body)

    def testModifyOceanRule(self):
        a = Auth(username, pwd)
        body = {
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.modifyOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'modifyOceanRule', body)

    def testDescribeOceanRule(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        oceanbase = Oceanbase(a)
        r = oceanbase.describeOceanRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'describeOceanRule', body)

    def testDeleteOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [],
            'type': '',
            'force': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.deleteOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'deleteOceanRule', body)

    def testResumeOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.resumeOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'resumeOceanRule', body)

    def testStopOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.stopOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'stopOceanRule', body)

    def testRestartOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.restartOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'restartOceanRule', body)

    def testStartAnalysisOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.startAnalysisOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'startAnalysisOceanRule', body)

    def testStopAnalysisOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.stopAnalysisOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'stopAnalysisOceanRule', body)

    def testResetOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.resetOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'resetOceanRule', body)

    def testStopAndStopAnalysisOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.stopAndStopAnalysisOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'stopAndStopAnalysisOceanRule', body)

    def testStopScheduleOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.stopScheduleOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'stopScheduleOceanRule', body)

    def testStartScheduleOceanRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': [],
            'operate': '',
            'scn': 0,
        }

        oceanbase = Oceanbase(a)
        r = oceanbase.startScheduleOceanRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'startScheduleOceanRule', body)

    def testListOceanRuleLog(self):
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

        oceanbase = Oceanbase(a)
        r = oceanbase.listOceanRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Oceanbase', 'listOceanRuleLog', body)


if __name__ == '__main__':
    unittest.main()
