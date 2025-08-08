# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.timing.TimingBackup import TimingBackup
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


class TimingBackupTestCase(unittest.TestCase):

    def testDescribeTimingBackupMssqlSource(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '22D03E06-94D0-5E2C-336E-4BEEC2D28EC4',
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.describeTimingBackupMssqlSource(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'describeTimingBackupMssqlSource', body)
    # 无用接口
    # def testVerifyTimingBackupOracleInfo(self):
    #     a = Auth(username, pwd)
    #     body = {
    #         'oracle_settings': {
    #             'ora_sid_name': '',
    #             'ora_port': 1,
    #             'ora_home_path': '',
    #             'ora_passwd': 'Info1234',
    #         },
    #         'wk_uuid': '',
    #     }
    #     timingBackup = TimingBackup(a)
    #     r = timingBackup.verifyTimingBackupOracleInfo(body)
    #     print(r[0])
    #     assert r[0]['ret'] == 200
    #     write(r[0], 'TimingBackup', 'verifyTimingBackupOracleInfo', body)

    # def testDescribeTimingBackupOracleContent(self):
    #     a = Auth(username, pwd)
    #     body = {
    #         'oracle_settings': {
    #
    #             'ora_passwd': 'Info1234',
    #             'ora_port': 1,
    #             'ora_sid_name': '',
    #             'ora_content_type': 0
    #         },
    #         'src_node_uuid': '',
    #     }
    #     timingBackup = TimingBackup(a)
    #     r = timingBackup.describeTimingBackupOracleContent(body)
    #     print(r[0])
    #     assert r[0]['ret'] == 200
    #     write(r[0], 'TimingBackup', 'describeTimingBackupOracleContent', body)

    def testDescibeTimingBackupOracleSriptPath(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': 'B61C4858-748D-0253-0F2F-76669902A53D',
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.descibeTimingBackupOracleSriptPath(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'descibeTimingBackupOracleSriptPath', body)

    def testDescibeDmDbInfo(self):
        a = Auth(username, pwd)
        body = {
            'dm_home': '',
            'host': '',
            'port': '',
            'user': '',
            'password': '',
            'type': 1,
            'schema_name': '',
            'node_uuid': '',
        }

        timingBackup = TimingBackup(a)
        r = timingBackup.descibeDmDbInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'descibeDmDbInfo', body)

    def testListTimingBackupMssqlDbList(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '22D03E06-94D0-5E2C-336E-4BEEC2D28EC4',
            'mssql_settings': {
                'win_verify': 0,
                'instance_name': 'MSSQLSERVER',
                'pass_word': '123456',
                'data_source': 'WIN-EGKN86NF3PM',
                'user_id': 'sa'
            }
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.listTimingBackupMssqlDbList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'listTimingBackupMssqlDbList', body)

    def testCreateTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'timing_backup': {
                'mirr_sync_attr': 1,
                'secret_key': '',
                'oracle_settings': {
                    'ora_sid_name': '',
                    'ora_content_type': 0,
                    'ora_use_script': 0,
                    'ora_port': 1,
                    'ora_script_path': '',
                    'ora_passwd': 'Info1234',
                    'ora_home_path': '',
                },
                'wk_data_type': 1,
                'task_name': 'testTiming',
                'backup_type': 0,
                'del_policy': 0,
                'mirr_sync_flag': 0,
                'snap_type': 0,
                'oracle_rman_settings': {
                    'rman_skip_offline': 0,
                    'rman_num_streams_arch': 20,
                    'rman_del_arch': 1,
                    'rman_include_arch_flag': 1,
                    'rman_num_streams_df': 1,
                    'rman_filespertset_arch': 20,
                    'rman_maxsetsize_df': 0,
                    'rman_set_limit_arch_flag': 0,
                    'rman_skip_readonly': 0,
                    'rman_maxsetsize_arch': 0,
                    'rman_cold_bkup': 0,
                    'rman_filespertset_df': 20,
                },
                'compress': 0,
                'encrypt_switch': 0,
                'wk_path': ['E:\\test\\', ],
                'excl_path': [],
                'bk_data_type': 1,
                'mirr_blk_size': 0,
                'bk_path': ['E:\\t\\', ],
                'blk_direct_copy': 0,
                'mirr_open_type': 0,
                'mssql_settings': {
                    'instance_name': 'MSSQLSERVER',
                    'time_out': '',
                    'data_source': '',
                    'win_verify': 1,
                    'user_id': '',
                    'db_name': '',
                    'pass_word': '',
                    'check_out': 1
                },
                'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                'bkup_policy': 2,
                'bkup_window': {
                    'sched_time_start': '00:00',
                    'sched_time_end': '00:00'
                },
                'bkup_one_time': 1547538235,
                'bkup_schedule': [
                    {
                        'limit': 32,
                        'sched_day': 7,
                        'sched_every': 2,
                        'sched_time': '18:34',
                        'sched_gap_min': 56
                    }
                ],
                'task_type': 0,
                'file_check_dir': '',
            },
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.createTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'createTimingBackup', body)

    def testDescribeTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': 'C04AE9FD-23A9-E389-61B2-89EF4D145DA2'
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.describeTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'describeTimingBackup', body)

    def testModifyTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': 'C04AE9FD-23A9-E389-61B2-89EF4D145DA2',
            'timing_backup': {
                'mirr_sync_attr': 1,
                'secret_key': '',
                'oracle_settings': {
                    'ora_sid_name': '',
                    'ora_content_type': 0,
                    'ora_use_script': 0,
                    'ora_port': 1,
                    'ora_script_path': '',
                    'ora_passwd': 'Info1234',
                    'ora_home_path': '',
                },
                'policy_uuid': '38FFA6E2-2A40-31D6-7A94-E8168EBA9FF1',
                'wk_data_type': 0,
                'task_name': 'testTiming',
                'backup_type': 1,
                'del_policy': 0,
                'mirr_sync_flag': 0,
                'snap_type': 0,
                'oracle_rman_settings': {
                    'rman_skip_offline': 0,
                    'rman_num_streams_arch': 1,
                    'rman_del_arch': 1,
                    'rman_include_arch_flag': 1,
                    'rman_num_streams_df': 1,
                    'rman_filespertset_arch': 20,
                    'rman_maxsetsize_df': 0,
                    'rman_set_limit_arch_flag': 0,
                    'rman_skip_readonly': 0,
                    'rman_maxsetsize_arch': 0,
                    'rman_cold_bkup': 0,
                    'rman_filespertset_df': 20,
                },
                'compress': 0,
                'encrypt_switch': 0,
                'wk_path': ['E:\\test\\', ],
                'excl_path': [],
                'bk_data_type': 1,
                'mirr_blk_size': 0,
                'bk_path': ['E:\\t\\', ],
                'blk_direct_copy': 0,
                'mirr_open_type': 0,
                'mssql_settings': {
                    'instance_name': '',
                    'time_out': '2',
                    'data_source': '',
                    'dbsize': '',
                    'win_verify': 0,
                    'user_id': '',
                    'db_name': '',
                    'pass_word': '',
                },
                'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                'bkup_policy': 0,
                'bkup_window': {
                    'sched_time_start': '15:18',
                    'sched_time_end': '14:37',
                },
                'bkup_one_time': 1515568566,
                'bkup_schedule': [
                    {
                        'limit': 25,
                        'sched_day': 24,
                        'sched_every': 2,
                        'sched_time': '04:07',
                        'sched_gap_min': 49,
                    }
                ],
                'task_type': 0,
                'random_str': '',
            },
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.modifyTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'modifyTimingBackup', body)

    def testListTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'search_field': '',
            'limit': 10,
            'page': 1,
            'search_value': '',
            'type': 0,
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.listTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'listTimingBackup', body)

    def testListTimingBackupStatus(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': [
                 '11111111-1111-1111-1111-111111111111'
            ],
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.listTimingBackupStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'listTimingBackupStatus', body)

    def testDeleteTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': [
                 'C04AE9FD-23A9-E389-61B2-89EF4D145DA2'
            ],
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.deleteTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'deleteTimingBackup', body)

    def testStartTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'task_uuids': [
                'C04AE9FD-23A9-E389-61B2-89EF4D145DA2'
            ],
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.startTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'startTimingBackup', body)

    def testStopTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'task_uuids': [
                'C04AE9FD-23A9-E389-61B2-89EF4D145DA2'
            ],
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.stopTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'stopTimingBackup', body)

    def testStartImmediateTimingBackup(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start_immediate',
            'task_uuids': [
                'C04AE9FD-23A9-E389-61B2-89EF4D145DA2'
            ],
        }
        timingBackup = TimingBackup(a)
        r = timingBackup.startImmediateTimingBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'startImmediateTimingBackup', body)

    def testVerifyTimingBackupOracleInfo(self):
        a = Auth(username, pwd)
        body = {
            'oracle_settings': {
            'ora_sid_name': '',
            'ora_port': 1,
            'ora_home_path': '',
            'ora_passwd': 'Info1234',},
            'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
        }

        timingBackup = TimingBackup(a)
        r = timingBackup.verifyTimingBackupOracleInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'verifyTimingBackupOracleInfo', body)

    def testDescribeTimingBackupOracleContent(self):
        a = Auth(username, pwd)
        body = {
            'oracle_settings': {
            'ora_passwd': 'Info1234',
            'ora_port': 1,
            'ora_sid_name': '',
            'ora_content_type': 0,},
            'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
        }

        timingBackup = TimingBackup(a)
        r = timingBackup.describeTimingBackupOracleContent(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'describeTimingBackupOracleContent', body)

    def testShowTimingBackupDetailInfo(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '',
            'timing_type': 3,
        }

        timingBackup = TimingBackup(a)
        r = timingBackup.showTimingBackupDetailInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'showTimingBackupDetailInfo', body)

    def testVerifyTimingBackupOracleLogin(self):
        a = Auth(username, pwd)
        body = {
            'wk_uuid': '',
            'oracle_settings': {
            'ora_sid_name': '',
            'ora_login_name': '',
            'ora_login_pwd': '',
            'ora_server_name': '',
            'ora_server_port': '',},
        }

        timingBackup = TimingBackup(a)
        r = timingBackup.verifyTimingBackupOracleLogin(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingBackup', 'verifyTimingBackupOracleLogin', body)


if __name__ == '__main__':
    unittest.main()
