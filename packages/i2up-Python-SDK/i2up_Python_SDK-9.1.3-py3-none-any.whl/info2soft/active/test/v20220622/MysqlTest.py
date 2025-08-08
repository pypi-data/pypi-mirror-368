
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.active.v20220622.Mysql import Mysql
# from info2soft.active.v20200722.Mysql import Mysql
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
pwd = '12345678'


class MysqlTestCase(unittest.TestCase):

    def testCreateStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'mysql_name': 1,
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'oracle',
            'start_rule_now': 0,
            'dbmap_topic': '',
            'map_type': 'table',
            'tab_map': [{
            'src_table': 'src_table',
            'dst_table': 'dst_table',
            'src_db': '111',
            'dst_db': '222',},],
            'full_sync': 0,
            'incre_sync': 1,
            'model_type': '1:0',
            'full_sync_mode': 'auto',
            'db_set': {
            'binlog_format': 'row',
            'binlog_row_image': 'full',
            'default_storage_engine': 'innoDB',
            'sync_binlog': '1',
            'innodb_flush_log': '2',
            'innodb_flush_method': 'O_DIRECT',
            'max_allowed_packet': '52',
            'open_files_limit': '65535',
            'server_id': '123456',
            'expire_logs_days': '7',
            'nat_mode': 0,
            'ip': '',},
            'full_sync_set': {
            'support_ddl': 1,
            'change_tf_path': '',
            'tf_file_save_time': 7,
            'nat_mode': 0,
            'foreign_ip': '',
            'extraction': 0,
            'start_lsn': 1,},
            'primary_db_one': '',
            'primary_map_type_one': '',
            'primary_map_one': '',
            'primary_db_two': '',
            'primary_map_type_two': '',
            'primary_map_two': '',
            'db_map': [{
            'dst_table': '',
            'src_table': '',},],
            'modify': '',
            'start_src_db_set': 0,
            'dst_db_set': {
            'binlog_format': '',
            'binlog_row_image': '',
            'default_storage_engine': '',
            'sync_binlog': '',
            'innodb_flush_log': '',
            'innodb_flush_method': '',
            'max_allowed_packet': '',
            'open_files_limit': '',
            'server_id': '',
            'expire_logs_days': '',
            'nat_mode': 1,
            'ip': '',},
            'dst_full_sync_set': {
            'support_ddl': 1,
            'change_tf_path': '',
            'tf_file_save_time': '',
            'nat_mode': '',
            'foreign_ip': '',
            'extraction': 0,
            'start_lsn': 1,},
            'start_dst_db_set': 0,
        }
        
        mysql = Mysql(a)
        r = mysql.createStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'createStreamRule', body)

    def testDeleteStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'mysql_uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.deleteStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteStreamRule', body)

    def testResartStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'restart',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.restartStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'restartStreamRule', body)

    def testResumeStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'resume',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.resumeStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'resumeStreamRule', body)

    def testStopStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.stopStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopStreamRule', body)

    def testModifyStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'modify',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.modifyStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'modifyStreamRule', body)

    def testStartParsingStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.startParsingStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'startParsingStreamRule', body)

    def testStopParsingStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.stopParsingStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopParsingStreamRule', body)

    def testResetParsingStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.resetParsingStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'resetParsingStreamRule', body)

    def testStartLoadStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.startLoadStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'startLoadStreamRule', body)

    def testStopLoadStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.stopLoadStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopLoadStreamRule', body)

    def testResetLoadStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.resetLoadStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'resetLoadStreamRule', body)

    def testRemoveStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.removeStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'removeStreamRule', body)

    def testStopScheduleStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.stopScheduleStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopScheduleStreamRule', body)

    def testStartScheduleStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.startScheduleStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'startScheduleStreamRule', body)

    def testStopAnalysisStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.stopAnalysisStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopAnalysisStreamRule', body)

    def testStartAnalysisStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.startAnalysisStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'startAnalysisStreamRule', body)

    def testResetAnalysisStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'mysql_uuid': '',
            'scn': '',
            'tf': '',
        }

        mysql = Mysql(a)
        r = mysql.resetAnalysisStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'resetAnalysisStreamRule', body)

    def testListStreamRules(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'where_args': {
            'mysql_uuid': '',},
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamRules', body)

    def testListStreamStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamStatus', body)

    def testListStreamLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'mysql_uuid': '9e59Fd51-EE1A-Ccf1-a972-f53f0eCa59B2',
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamLog', body)

    def testListStreamSyncStatus(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '3dfE3CB4-5654-9BEE-cCf9-15fDdAecDB3F',
            'mysql_uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamSyncStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamSyncStatus', body)

    def testDescribeHistory(self):
        a = Auth(username, pwd)
        body = {
            'mysql_uuid': 'aAAAEAeB-733F-2dbb-2CaB-CDEfFf3ED9af',
            'start_time': '2019-10-11 14:23:13',
            'end_time': '2019-10-11 15:23:13',
        }
        
        mysql = Mysql(a)
        r = mysql.describeHistory(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeHistory', body)

    def testDescribeResource(self):
        a = Auth(username, pwd)
        body = {
            'set_time': 1,
            'type': '',
            'interval': '时间间隔',
            'set_time_init': '',
            'rule_uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.describeResource(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeResource', body)

    def testModifyStreamRule(self):
        a = Auth(username, pwd)
        body = {
            'mysql_name': 'mysql',
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'kafka',
            'start_rule_now': 0,
            'node_uuid': ' 6B1153F6-DAD9-BC39-888A-A743FCC208E6',
            'dbmap_topic': '',
            'map_type': 'table',
            'tab_map': [{
            'src_table': 'src_table',
            'topic': 'topic',},],
            'full_sync': 0,
            'incre_sync': 1,
            'model_type': '1:0',
            'full_sync_mode': 'auto',
            'db_set': {
            'db_node': '1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'binlog_format': 'row',
            'binlog_row_image': 'full',
            'default_storage_engine': 'innoDB',
            'sync_binlog': '1',
            'innodb_flush_log': '2',
            'innodb_flush_method': 'O_DIRECT',
            'max_allowed_packet': '52',
            'open_files_limit': '65535',
            'server_id': '123456',
            'expire_logs_days': '7',
            'nat_mode': 0,
            'ip': '',},
            'full_sync_set': {
            'support_ddl': 1,
            'node': ' 6B1153F6-DAD9-BC39-888A-A743FCC208E6',
            'change_tf_path': '',
            'tf_file_save_time': 7,
            'nat_mode': 0,
            'foreign_ip': '',},
            'primary_node_one': '',
            'primary_node_two': '',
            'primary_db_one': '',
            'primary_map_type_one': '',
            'primary_map_one': [],
            'primary_db_two': '',
            'primary_map_type_two': '',
            'primary_map_two': [],
            'db_map': [{
            'src_db': 'src_db',
            'dst_db': 'dst_db',},],
            'mysql_uuid': '5349E2CF-7DBO-OAF2-13CB-BB7DFD8A9D86',
        }
        
        mysql = Mysql(a)
        r = mysql.modifyStreamRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'modifyStreamRule', body)

    def testDescribeStreamRules(self):
        a = Auth(username, pwd)
        body = {
            'mysql_uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mysql = Mysql(a)
        r = mysql.describeStreamRules(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeStreamRules', body)

    def testCreateStreamCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_name': 'ctt->ctt',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cmp_type': 'table, database, all',
            'db_user_map': {
            'CTT': 'CTT',},
            'filter_table': [
            '用户.表名',],
            'db_tb_map': '表映射',
            'dump_thd': 1,
            'rule_uuid': 'b19DA68C-63ca-4e87-b0Fc-A38BFA7bbabD',
            'polices': '"0|00:00',
            'policy_type': 'one_time',
            'try_split_part_table': 0,
            'one_time': '',
            'concurrent_table': [],
            'repair': 1,
            'fix_related': 1,
        }
        
        mysql = Mysql(a)
        r = mysql.createStreamCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'createStreamCmp', body)

    def testDescribeStreamCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mysql = Mysql(a)
        r = mysql.describeStreamCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeStreamCmp', body)

    def testDeleteStreamRules(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '25E74fa8-1BE8-Cf55-8b2a-27F1f72c7eAb',
        }
        
        mysql = Mysql(a)
        r = mysql.deleteStreamRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteStreamRules', body)

    def testListStreamCmps(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamCmps(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamCmps', body)

    def testListStreamCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.listStreamCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listStreamCmpStatus', body)

    def testDeleteCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'time_list': 'D1Ae87Bb-b589-CD63-afcd-D3DfebcFEc17',
            'uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.deleteCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteCmpResult', body)

    def testListCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'limit': '',
            'offset': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listCmpResult', body)

    def testDescribeTbCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': '212dc6dD-42AD-e95D-d2bf-14edcbb52C47',
            'start_time': '',
        }
        
        mysql = Mysql(a)
        r = mysql.describeTbCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeTbCmpResult', body)

    def testDescribeCmpErrorMsg(self):
        a = Auth(username, pwd)
        body = {
            'offset': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
            'uuid': 'cEb95b0A-7F69-28d9-fD29-235AAE85B66e',
            'start_time': '',
            'name': '',
            'owner': 'admin',
        }
        
        mysql = Mysql(a)
        r = mysql.describeCmpErrorMsg(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeCmpErrorMsg', body)

    def testListFixResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listFixResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listFixResult', body)

    def testExportCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.exportCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'exportCmpResult', body)

    def testListCmpDiffMap(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'time': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listCmpDiffMap(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listCmpDiffMap', body)

    def testCreateBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'mysql_uuid': '0A2fAF41-c0D4-1F83-4427-556bd385F220',
            'start_val': 1000,
            'scan_ip': [
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',
            'c01D7F86-A631-b79f-E2AA-7ccb7f2bE851',],
            'hosts': [{
            'ip': '192.168.12.200',
            'password': '',},],
            'use_ip_sw': 1,
        }
        
        mysql = Mysql(a)
        r = mysql.createBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'createBkTakeover', body)

    def testDescribeBkTakeover(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mysql = Mysql(a)
        r = mysql.describeBkTakeover(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeBkTakeover', body)

    def testCreateObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'db_user_map': '{"src_user":"dst_user"}',
            'policies': '',
            'policy_type': 'periodic',
            'one_time': '2019-05-27 16:07:08',
            'repair': 1,
            'obj_cmp_name': 'test',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'cal_table_recoders': 1,
            'cmp_type': 'user',
            'rule_uuid': '751A03F5-C97D-645B-82B2-316A5D198528',
        }
        
        mysql = Mysql(a)
        r = mysql.createObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'createObjCmp', body)

    def testDeleteBkTakeover(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.deleteBkTakeover(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteBkTakeover', body)

    def testListTakeoverResult(self):
        a = Auth(username, pwd)
        body = {
            'bk_takeover_uuid': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listTakeoverResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listTakeoverResult', body)

    def testListTakeoverStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.listTakeoverStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listTakeoverStatus', body)

    def testListTakeoverList(self):
        a = Auth(username, pwd)
        body = {
        }
        
        mysql = Mysql(a)
        r = mysql.listTakeoverList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listTakeoverList', body)

    def testCreateObjFix(self):
        a = Auth(username, pwd)
        body = {
            'obj_fix_name': 'test',
            'src_db_uuid': '4CA773F4-36E3-A091-122C-ACDFB2112C21',
            'tgt_db_uuid': '40405FD3-DB86-DC8A-81C9-C137B6FDECE5',
            'rule_uuid': '751A03F5-C97D-645B-82B2-316A5D198528',
            'obj_map': [{
            'type': 'owner.name',},{
            'type': 'owner.name',},],
        }
        
        mysql = Mysql(a)
        r = mysql.createObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'createObjFix', body)

    def testDescribeObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '052fAdA4-d9EE-7468-D6d2-ACB237D83BeE',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mysql = Mysql(a)
        r = mysql.describeObjFix(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeObjFix', body)

    def testDeleteObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '34AfBABc-f6D4-D522-f0de-90F42dDcb4c3',
        }
        
        mysql = Mysql(a)
        r = mysql.deleteObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteObjFix', body)

    def testListObjFix(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjFix', body)

    def testDescribeObjFixResult(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '29dD5bEb-b59F-e1DB-9766-2C574DccbB0b',
        }
        
        mysql = Mysql(a)
        r = mysql.describeObjFixResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeObjFixResult', body)

    def testListObjFixStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.listObjFixStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjFixStatus', body)

    def testRestartObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'operate': ''
        }

        mysql = Mysql(a)
        r = mysql.restartObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'restartObjFix', body)

    def teststopObjFix(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
            'operate': ''
        }

        mysql = Mysql(a)
        r = mysql.stopObjFix(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'stopObjFix', body)

    def testListObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        mysql = Mysql(a)
        r = mysql.listObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjCmp', body)

    def testDescribeObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'E9bA4e43-cE72-1a7f-6F12-eAC69Dff2A65',
            'time_list': [],
        }
        
        mysql = Mysql(a)
        r = mysql.describeObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeObjCmpResultTimeList', body)

    def testDescribeObjCmp(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        mysql = Mysql(a)
        r = mysql.describeObjCmp(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeObjCmp', body)

    def testListObjCmpResultTimeList(self):
        a = Auth(username, pwd)
        body = {
            'uuid': 'e1CdbB6F-bBDf-eB0F-3caB-63e85A89209e',
        }
        
        mysql = Mysql(a)
        r = mysql.listObjCmpResultTimeList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjCmpResultTimeList', body)

    def testDeleteObjCmp(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        mysql = Mysql(a)
        r = mysql.deleteObjCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'deleteObjCmp', body)

    def testListObjCmpStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        mysql = Mysql(a)
        r = mysql.listObjCmpStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjCmpStatus', body)

    def testListObjCmpCmpInfo(self):
        a = Auth(username, pwd)
        body = {
            'filed': '',
            'uuid': '',
            'start_time': '',
            'offset': 1,
            'limit': 10,
            'search_value': '',
            'usr': 'I2',
        }
        
        mysql = Mysql(a)
        r = mysql.listObjCmpCmpInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'listObjCmpCmpInfo', body)

    def testDescribeObjCmpResult(self):
        a = Auth(username, pwd)
        body = {
            'BackLackOnly': 0,
            'uuid': 'fce8efF9-2B4c-EBDE-AC17-6f3DC3Ff851D',
            'start_time': '',
            'limit': 1,
            'offset': '',
            'search_value': '',
        }
        
        mysql = Mysql(a)
        r = mysql.describeObjCmpResult(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'describeObjCmpResult', body)

    def testCmpStopStreamCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': 'bDa7dFA5-7C84-6FB6-6Cd0-B3f264f6DC34',
            'operate': 'cmp_stop',
        }

        mysql = Mysql(a)
        r = mysql.cmpStopStreamCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'cmpStopStreamCmp', body)

    def testCmpRestartStreamCmp(self):
        a = Auth(username, pwd)
        body = {
            'tb_cmp_uuids': 'bDa7dFA5-7C84-6FB6-6Cd0-B3f264f6DC34',
            'operate': 'cmp_restart',
        }

        mysql = Mysql(a)
        r = mysql.cmpRestartStreamCmp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Mysql', 'cmpRestartStreamCmp', body)


if __name__ == '__main__':
    unittest.main()
