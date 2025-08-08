# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.active.v20220622.DataChk import DataChk
# from info2soft.active.v20200722.DataChk import DataChk
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


class DataChkTestCase(unittest.TestCase):

    def testCreateTbCmp(self):
        a = Auth(username, pwd)
        body = {
                   'tb_cmp_name': 'ctt->ctt',
                   'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
                   'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
                   'cmp_type': 'table',
                   'filter_table': '[用户.表名]',
                   'db_tb_map': '表映射',
                   'dump_thd': 1,
                   'polices': '"0|00:00',
                   'policy_type': 'one_time',
                   'concurrent_table': [
                       'hh.ww', ],
                   'try_split_part_table': 0,
                   'one_time': '2019-05-27 16:07:08',
                   'config': {
                       'data_select': [{
                           'src_user': '',
                           'src_tb': '',
                           'src_query': '',
                           'dst_user': '',
                           'dst_tb': '',
                           'dst_query': '', }, ],
                       'compare_key': [{
                           'src_user': '',
                           'src_tb': '',
                           'dst_user': '',
                           'dst_tb': '',
                           'src_dst_key': '', }, ],
                       'globalConfig': {
                           'dkdiff_enable_step_count_table': '',
                           'dkdbsource_diff_only_key_columns': '',
                       'dkmagic_plan_max_diffs': 10000,
                       'dkfilesink_enable_sqlpatch_file': '',
                   'dkmagic_plan_number_tolerance_type': 'absolute',
                   'dkmagic_plan_number_tolerance': 1,
                   'dkmagic_plan_datetime_tolerance': 1,
                   'split_table_schedule_cron': '',
                   'split_table_single_segment_max_rows': 5000000,
                   'split_table_result_expire_in_seconds': 0,
                   'dkdiffengine_recursion_max_steps': 1,
                   'dkdiffengine_recursion_interval_step_delay': 0,
                   'dkdbsource_left_ignore_type_names': '‘’',
                   'dkdbsource_right_ignore_type_names': '‘’',
                   'dkdbsource_left_ignore_column_names': '‘’',
                   'dkdbsource_right_ignore_column_names': '',
                   'globalconfig': [{
                       'key': '',
                       'value': '', }, ],
                   'tolerance': '', },
        'globals': [{
            'src_user': '',
            'dst_user': '',
            'src_query': '',
            'dst_query': '', }, ],
        'exclude_tables': [{
            'src_user': '',
            'src_tb': '',
            'dst_user': '',
            'dst_tb': '', }, ],
        'timestamps': {
            'column_name': '',
            'back_delay_in_seconds': 1,
            'end_time': '', },
        'global_time_limit': '', },
        }

        dataChk = DataChk(a)
        r = dataChk.createTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'createTbCmp', body)

    def testDescribeTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '3D3c7Fbc-da44-BDD2-cCdE-dbB5dc21ef8F',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dataChk = DataChk(a)
        r = dataChk.describeTbCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmp', body)

    def testDeleteTbCmp(self):
        a = Auth(username, pwd)
        body = {
                   'force': '',
               'uuids': 'A1AdAf11-BBA1-11f1-a8aC-7E44bE8BBDb3'
        }

        dataChk = DataChk(a)
        r = dataChk.deleteTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'deleteTbCmp', body)

    def testListTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }

        dataChk = DataChk(a)
        r = dataChk.listTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'listTbCmp', body)

    def testListTbCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        dataChk = DataChk(a)
        r = dataChk.listTbCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'listTbCmpResultTimeList', body)

    def testStopTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'tb_cmp_uuids': 'eff2C655-5f9B-2d3e-2eCA-D73Bf976D982',
        }

        dataChk = DataChk(a)
        r = dataChk.stopTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'stopTbCmp', body)

    def testRestartTbCmp(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'tb_cmp_uuids': 'eff2C655-5f9B-2d3e-2eCA-D73Bf976D982',
        }

        dataChk = DataChk(a)
        r = dataChk.restartTbCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'restartTbCmp', body)

    def testDescribeTbCmpResuluTimeList(self):
        a = Auth(username, pwd)
        body = {
            'time_list': 'cbD2EA8b-f83D-0cea-bb35-e4eDbe62BEA3',
            'uuid': '',
        }

        dataChk = DataChk(a)
        r = dataChk.describeTbCmpResuluTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmpResuluTimeList', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'A7DE1FC2-DfAE-FC91-18f2-1CcF8FBEf8cC',
            'start_time': '',
            'flag': 1,
        }

        dataChk = DataChk(a)
        r = dataChk.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmpResult', body)

    def testDescribeTbCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'B7CBcC47-807b-8Cb8-a347-cbEc24fBEBBC',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }

        dataChk = DataChk(a)
        r = dataChk.describeTbCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmpErrorMsg', body)

    def testDescribeTbCmpCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }

        dataChk = DataChk(a)
        r = dataChk.describeTbCmpCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmpCmpResult', body)

    def testDescribeTbCmpCmpDesc(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'b1E1d998-3a61-f4e3-F7Ff-D3D0192EfC85',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        dataChk = DataChk(a)
        r = dataChk.describeTbCmpCmpDesc(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'DataChk', 'describeTbCmpCmpDesc', body)


if __name__ == '__main__':
    unittest.main()
