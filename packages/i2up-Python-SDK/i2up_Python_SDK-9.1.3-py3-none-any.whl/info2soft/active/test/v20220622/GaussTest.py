
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.active.v20220622.Gauss import Gauss
# from info2soft.active.v20200722.Gauss import Gauss
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


class GaussTestCase(unittest.TestCase):

    def testCreateGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'map_type': 'user',
            'table_map': [],
            'dbmap_topic': '',
            'sync_mode': 1,
            'start_scn': 1,
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_mode': 'direct',
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],},
            'inc_sync_ddl_filter': {},
            'filter_table_settings': {
            'exclude_table': [
            'hh.ww',],},
            'etl_settings': {
            'etl_table': [{
            'oprType': 'IRP',
            'table': '',
            'user': '',
            'process': 'SKIP',
            'addInfo': '',},],},
            'start_rule_now': 0,
            'storage_settings': {
            'src_max_mem': 512,
            'src_max_disk': 5000,
            'txn_max_mem': 10000,
            'tf_max_size': 100,
            'tgt_extern_table': '',},
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',},
            'table_space_map': {
            'tgt_table_space': '',
            'table_mapping_way': 'ptop',
            'table_path_map': {
            'ddd': 'sss',
            'ddd1': 'sss1',},
            'table_space_name': {
            'qq': 'ss',},},
            'other_settings': {
            'keep_dyn_data': 0,
            'dyn_thread': 1,
            'dly_constraint_load': 0,
            'zip_level': 0,
            'ddl_cv': 0,
            'keep_bad_act': 0,
            'keep_usr_pwd': 1,
            'convert_urp_of_key': 0,
            'ignore_foreign_key': 0,},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'kafka_time_out': '',
            'part_load_balance': '',
        }
        
        gauss = Gauss(a)
        r = gauss.createGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'createGaussRule', body)

    def testModifyGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': 'ctt->ctt',
            'src_db_uuid': ' 1B1153F6-DAD9-BC39-888A-A743FCC208E5',
            'tgt_db_uuid': ' D42BF707-C971-EEA9-521F-BB0F3F7A92FC',
            'tgt_type': 'oracle',
            'db_user_map': {
            'CTT': 'CTT',},
            'map_type': 'user',
            'table_map': [],
            'dbmap_topic': '',
            'sync_mode': 1,
            'start_scn': 1,
            'full_sync_settings': {
            'keep_exist_table': 0,
            'keep_table': 0,
            'load_mode': 'direct',
            'ld_dir_opt': 0,
            'his_thread': 1,
            'try_split_part_table': 0,
            'concurrent_table': [
            'hello.world',],},
            'inc_sync_ddl_filter': {},
            'filter_table_settings': {
            'exclude_table': [
            'hh.ww',],},
            'etl_settings': {
            'etl_table': [{
            'oprType': 'IRP',
            'table': '',
            'user': '',
            'process': 'SKIP',
            'addInfo': '',},],},
            'start_rule_now': 0,
            'storage_settings': {
            'src_max_mem': 512,
            'src_max_disk': 5000,
            'txn_max_mem': 10000,
            'tf_max_size': 100,
            'tgt_extern_table': '',},
            'error_handling': {
            'load_err_set': 'continue',
            'drp': 'ignore',
            'irp': 'irpafterdel',
            'urp': 'toirp',},
            'table_space_map': {
            'tgt_table_space': '',
            'table_mapping_way': 'ptop',
            'table_path_map': {
            'ddd': 'sss',
            'ddd1': 'sss1',},
            'table_space_name': {
            'qq': 'ss',},},
            'other_settings': {
            'keep_dyn_data': 0,
            'dyn_thread': 1,
            'dly_constraint_load': 0,
            'zip_level': 0,
            'ddl_cv': 0,
            'keep_bad_act': 0,
            'keep_usr_pwd': 1,
            'convert_urp_of_key': 0,
            'ignore_foreign_key': 0,},
            'bw_settings': {
            'bw_limit': '"12*00:00-13:00*40M,3*00:00-13:00*40M"',},
            'biz_grp_list': [],
            'kafka_time_out': '',
            'part_load_balance': '',
            'rule_uuid': '',
        }
        
        gauss = Gauss(a)
        r = gauss.modifyGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'modifyGaussRule', body)

    def testDeleteGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'type': '',
        }
        
        gauss = Gauss(a)
        r = gauss.deleteGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'deleteGaussRule', body)

    def testResumeGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'operate': '',
        }

        gauss = Gauss(a)
        r = gauss.resumeGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'resumeGaussRule', body)

    def testStopGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'operate': '',
        }

        gauss = Gauss(a)
        r = gauss.stopGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'stopGaussRule', body)

    def testRestartGaussRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [
            'DBED8CDE-435D-7865-76FE-149AA54AC7F7',],
            'operate': '',
        }

        gauss = Gauss(a)
        r = gauss.restartGaussRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'restartGaussRule', body)

    def testListGaussRules(self):
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
        
        gauss = Gauss(a)
        r = gauss.listGaussRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'listGaussRules', body)

    def testListGaussStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        gauss = Gauss(a)
        r = gauss.listGaussStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'listGaussStatus', body)

    def testDescribeGaussTraffic(self):
        a = Auth(username, pwd)
        body = {
            'set_time': 1,
            'type': '',
            'interval': '时间间隔',
            'set_time_init': '',
            'rule_uuid': '',
        }
        
        gauss = Gauss(a)
        r = gauss.describeGaussTraffic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'describeGaussTraffic', body)

    def testDescribeGuassRule(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        gauss = Gauss(a)
        r = gauss.describeGuassRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'describeGuassRule', body)

    def testDbCheckGuass(self):
        a = Auth(username, pwd)
        body = {
            'src_db_uuid': '',
            'dst_db_uuid': '',
        }

        gauss = Gauss(a)
        r = gauss.dbCheckGuass(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'dbCheckGuass', body)

    def testListGuassRuleLog(self):
        a = Auth(username, pwd)
        body = {
            'offset': 0,
            'limit': 10,
            'date_start': '',
            'date_end': '',
            'type': 1,
            'module_type': 1,
            'query_type': 1,
            'rule_uuid': 'B86bAd2C-e2B1-416F-fe7E-3d6b2175EC5d',
        }

        gauss = Gauss(a)
        r = gauss.listGuassRuleLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Gauss', 'listGuassRuleLog', body)


if __name__ == '__main__':
    unittest.main()
