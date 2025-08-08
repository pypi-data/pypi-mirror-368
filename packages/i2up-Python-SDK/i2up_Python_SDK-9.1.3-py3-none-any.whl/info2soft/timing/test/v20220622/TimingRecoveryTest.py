# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.timing.v20220622.TimingRecovery import TimingRecovery
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

    def testListTimingRecoveryMssqlTime(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'rc_data_path': 'E:\\mssqlBK\\ts-11111111-1111-1111-1111-111111111111\\',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryMssqlTime(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryMssqlTime', body)

    def testDescribeTimingRecoveryMssqlInitInfo(self):
        a = Auth(username, pwd)
        body = {
            'rc_point_in_time': '2017-12-21_13-16-53',
            'bk_uuid': '11111111-1111-1111-1111-111111111111',
            'rc_data_path': '',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeTimingRecoveryMssqlInitInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeTimingRecoveryMssqlInitInfo', body)

    def testListTimingRecoveryPathList(self):
        a = Auth(username, pwd)
        body = {
            'rc_data_path': 'E:\\test3\\',
            'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'backup_task_uuid': '',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryPathList(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryPathList', body)

    def testVerifyTimingRecoveryMssqlInfo(self):
        a = Auth(username, pwd)
        body = {
            'mssql_settings': {
                'win_verify': 0,
                'pass_word': '123456',
                'instance_name': 'MSSQLSERVER',
                'user_id': 'sa'
            },
            'wk_uuid': '22D03E06-94D0-5E2C-336E-4BEEC2D28EC4',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.verifyTimingRecoveryMssqlInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'verifyTimingRecoveryMssqlInfo', body)

    def testCreateTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'timing_recovery': {
                "wk_path": ["E:\\test\\"],
                "bk_path": ["E:\\t\\2019-01-15_15-49-00\\E\\test\\"],
                "rc_data_path": "E:\\t\\",
                "rc_style": 0,
                "task_name": "testTiming",
                "bk_uuid": "B8566905-411E-B2CD-A742-77B1346D8E84",
                "wk_uuid": "67E33CDB-D75B-15B3-367D-50C764F5A26F",
                "del_policy": 0,
                "bk_data_type": 1,
                "mirr_blk_size": "32768",
                "wk_data_type": 1,
                "encrypt_switch": 0,
                "secret_key": "",
                "compress": 0,
                "blk_direct_copy": 0,
                "snap_type": 0,
                "bkup_policy": 2,
                "bkup_one_time": 1547538235,
                "bkup_schedule": [
                    {
                        "limit": 32, "sched_day": 7, "sched_every": 2, "sched_time": "18:34", "sched_gap_min": 56
                    }
                ],
                "oracle_settings": {
                    "ora_sid_name": "",
                    "ora_content_type": 0,
                    "ora_use_script": 0,
                    "ora_port": 1,
                    "ora_script_path": "",
                    "ora_passwd": "Info1234",
                    "ora_home_path": ""
                },
                "mssql_settings": {
                    "instance_name": "MSSQLSERVER", "time_out": "", "data_source": "", "win_verify": 1,
                                   "user_id": "", "db_name": "", "pass_word": "", "check_out": 1
                },
                "rc_point_in_time": "2019-01-15_15-49-00", "username": "admin", "id": "new", "auto_start": 1,
                "backup_task_uuid": "11111111-1111-1111-1111-111111111111", "backup_type": 0, "create_time": 1547627546,
                "excl_path": [], "file_check_dir": "", "file_check_switch": "0", "full_copy": 0, "mirr_open_type": 0,
                "mirr_sync_attr": 1, "mirr_sync_flag": 0,
                "oracle_rman_settings": {
                    "rman_skip_offline": 0, "rman_num_streams_arch": 20, "rman_del_arch": 1,
                                         "rman_include_arch_flag": 1, "rman_num_streams_df": 1,
                                         "rman_filespertset_arch": 20, "rman_maxsetsize_df": 0,
                                         "rman_set_limit_arch_flag": 0, "rman_skip_readonly": 0,
                                         "rman_maxsetsize_arch": 0, "rman_cold_bkup": 0, "rman_filespertset_df": 20
                },
                "random_str": "11111111-1111-1111-1111-111111111111",
                "bk_path_policy": 0,
                "task_type": 0,
                "task_uuid": "11111111-1111-1111-1111-111111111111",
                "user_uuid": "1BCFCAA3-E3C8-3E28-BDC5-BE36FDC2B5DC",
                "bkup_window": {"sched_time_start": "00:00", "sched_time_end": "00:00"},
                "biz_grp_list": [],
                "biz_grp_name": []
            },
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.createTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'createTimingRecovery', body)

    def testModifyTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'timing_recovery': {
                'wk_uuid': '7AD64D7A-7D1D-AC51-5DF1-29A58345A288',
                'task_name': 'task',
                'random_str': '0DD4E727-70AB-62C6-BEB5-D012DFAE46E3',
                'wk_path': [],
                'bk_data_type': 1,
                'bk_path': [],
                'backup_type': 0,
                'oracle_settings': {
                    'ora_rc_point_thread': 1,
                    'ora_rc_point_date': '2017-12-21 13:26:00',
                    'ora_passwd': 'Info1234',
                    'ora_port': 1,
                    'ora_rc_point_type': 0,
                    'ora_do_recovery': 0,
                    'ora_do_restore': 0,
                    'ora_home_path': '',
                    'ora_rst_type': 0,
                    'ora_rst_limit_type': 0,
                    'ora_sid_name': '',
                    'ora_rst_limit_thread': 1,
                    'ora_rst_limit_date': '2017-12-21 13:26:00',
                    'ora_content_type': 0,
                    'ora_rst_limit_log_seq': '',
                    'ora_rst_limit_scn': 0,
                    'ora_rc_type': 0,
                    'ora_rc_point_log_seq': '',
                    'ora_rc_point_scn': 0,
                },
                'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                'task_uuid': '7AD64D7A-7D1D-AC51-5DF1-29A58345A288',
                'backup_task_uuid': '',
                'mssql_settings': {
                    'win_verify': 0,
                    'mdf_name': '',
                    'src_db_name': '',
                    'user_id': '',
                    'ldf_name': '',
                    'ldf_path': '',
                    'instance_name': '',
                    'pass_word': '',
                    'db_file_save_path': '',
                    'mdf_path': '',
                    'new_db_name': '',
                },
                'rc_data_path': 'C:\\back\\',
                'rc_style': 1,
                'wk_data_type': 0,
                'rc_point_in_time': '2017-12-21_13-16-53',
            },
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.modifyTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'modifyTimingRecovery', body)

    def testDescribeTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '11111111-1111-1111-1111-111111111111'
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeTimingRecovery', body)

    def testListTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'page': 1,
            'limit': 1,
            'search_field': '',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecovery', body)

    def testListTimingRecoveryStatus(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': [
                '11111111-1111-1111-1111-111111111111'
            ],
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryStatus', body)

    def testDeleteTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': [
                '11111111-1111-1111-1111-111111111111'
            ],
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.deleteTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'deleteTimingRecovery', body)

    def testStartTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': ['11111111-1111-1111-1111-111111111111'],
            'operate': 'start',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.startTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'startTimingRecovery', body)

    def testStopTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
            'task_uuids': ['11111111-1111-1111-1111-111111111111'],
            'operate': 'stop',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.stopTimingRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'stopTimingRecovery', body)

    def testListTimingRecoveryDb2Time(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'rc_data_path': 'E:\\mssqlBK\\ts-11111111-1111-1111-1111-111111111111\\',
        }
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryDb2Time(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryDb2Time', body)

    def testListTimingRecoveryOracleRcPointInfo(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
            'bk_uuid': '',
            'bk_path': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryOracleRcPointInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryOracleRcPointInfo', body)

    def testListTimingRecoveryDb(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'rc_data_path': 'E:/mssqlBK/ts-11111111-1111-1111-1111-111111111111/',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryDb(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryDb', body)

    def testListTimingRecoveryGaussTime(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'bk_path': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryGaussTime(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryGaussTime', body)

    def testDescribeTimingRecoveryDmBackupInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'bk_path': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeTimingRecoveryDmBackupInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeTimingRecoveryDmBackupInfo', body)

    def testOperateVolume(self):
        a = Auth(username, pwd)
        body = {
            'volume_uuid': '',
            'node_uuid': '',
            'operate': 'mount',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.operateVolume(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'operateVolume', body)

    def testListTimingBackupPoint(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingBackupPoint(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingBackupPoint', body)

    def testTaskMountDir(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
            'bakdir': '',
            'rc_point': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.taskMountDir(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'taskMountDir', body)

    def testDescribeGroupTimingRecovery(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeGroupTimingRecovery(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeGroupTimingRecovery', body)

    def testTimingRecoveryCheckDir(self):
        a = Auth(username, pwd)
        body = {
            'check_type': 1,
            'file_dir': [],
            'node_uuid': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.timingRecoveryCheckDir(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'timingRecoveryCheckDir', body)

    def testListTimingRecoveryDbInfo(self):
        a = Auth(username, pwd)
        body = {
            'rc_data_path': '',
            'bk_uuid': '',
            'wk_data_type': '4',
            'bk_storage': 1,
            'obs_settings': {},
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listTimingRecoveryDbInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listTimingRecoveryDbInfo', body)

    def testDescribeRcMysqlInfo(self):
        a = Auth(username, pwd)
        body = {
            'bk_uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
            'rc_data_path': 'E:\\mssqlBK\\ts-11111111-1111-1111-1111-111111111111\\',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeRcMysqlInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeRcMysqlInfo', body)

    def testListSbtContrlFile(self):
        a = Auth(username, pwd)
        body = {
            'rc_data_path': '',
            'ora_content_type': 1,
            'bk_uuid': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.listSbtContrlFile(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'listSbtContrlFile', body)

    def testDescribeSbtDbid(self):
        a = Auth(username, pwd)
        body = {
            'file_name': '',
            'bk_uuid': '',
        }

        timingRecovery = TimingRecovery(a)
        r = timingRecovery.describeSbtDbid(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'TimingRecovery', 'describeSbtDbid', body)


if __name__ == '__main__':
    unittest.main()
