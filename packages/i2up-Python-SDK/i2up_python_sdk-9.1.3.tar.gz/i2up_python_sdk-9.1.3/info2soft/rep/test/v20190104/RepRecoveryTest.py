
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.rep.v20181227.RepRecovery import RepRecovery
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
    
                
class RepRecoveryTestCase(unittest.TestCase):

    def testCreateRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rep_recovery': {
                'cdp_position': '2019-01-02_16-35-21+-2',
                'rc_name': 'rep_recovery',
                'cdp_time': '2019-01-02 16:35:21.0',
                'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                'snapshot_size': '1.34 GB',
                'cdp_rc_method': 0,
                'snapshot_time': '2017-11-17 17:24:14',
                'rc_type': 1,
                'snapshot_name': 'c5809dd2-e8be-4389-ac0d-0a657ff94da0_snap_2017-11-17_17-24-14',
                'bk_path': ['G:\\cdp2\\G\\cdp\\', ],
                'oph_policy': 0,
                'cdp_file': 'Baseline',
                'cdp_op': 'backup',
                'wk_path': ['G:\\cdp_rc\\', ],
                'rep_uuid': '051E0501-04EF-E1ED-0CEA-2E8751135CE4'
            },
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.createRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'createRepRecovery', body)

    def testDescribeRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rep_recovery': {
                'rc_uuid': '11111111-1111-1111-1111-111111111111'
            },
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.describeRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'describeRepRecovery', body)

    def testModifyRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rep_recovery': {
                'rc_uuid': '11111111-1111-1111-1111-111111111111',
                'cdp_position': '2017-11-17_15-30-40+-2',
                'rc_name': 'rep_recovery',
                'cdp_time': '2018-04-24 13:43:26.0',
                'wk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                'snapshot_size': '1.34 GB',
                'cdp_rc_method': 0,
                'snapshot_time': '2017-11-17 17:24:14',
                'rc_type': 0,
                'snapshot_name': 'c5809dd2-e8be-4389-ac0d-0a657ff94da0_snap_2017-11-17_17-24-14',
                'bk_path': ['G:\\cdp2\\G\\cdp\\', ],
                'oph_policy': 0,
                'cdp_file': 'Baseline',
                'cdp_op': 'backup',
                'wk_path': ['G:\\cdp_rc\\1', ],
                'rep_uuid': '051E0501-04EF-E1ED-0CEA-2E8751135CE4',
                'random_str': '',
            },
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.modifyRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'updateRepRecovery', body)

    def testDeleteRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rc_uuids': ['11111111-1111-1111-1111-111111111111'],
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.deleteRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'deleteRepRecovery', body)

    def testListRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'search_field': '',
            'search_value': '',
            'limit': 1,
            'type': 1,
            'page': 1,
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.listRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listRepRecovery', body)

    def testStartRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rc_type': 1,
            'rc_uuids': ['11111111-1111-1111-1111-111111111111',],
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.startRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'startRepRecovery', body)

    def testStopRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'rc_type': 1,
            'rc_uuids': ['11111111-1111-1111-1111-111111111111',],
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.stopRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'stopRepRecovery', body)

    def testClearFinishRepRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'clear_finish',
            'rc_type': 1,
            'rc_uuids': ['11111111-1111-1111-1111-111111111111',],
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.clearFinishRepRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'clearFinishRepRecovery', body)

    def testListRepRecoveryStatus(self):
        a = Auth(username, pwd)
        body = {
            'rc_uuids': ['11111111-1111-1111-1111-111111111111'],
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.listRepRecoveryStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listRepRecoveryStatus', body)

    def testListRepRecoveryCdpRange(self):
        a = Auth(username, pwd)
        body = {
            'rep_uuid': '051E0501-04EF-E1ED-0CEA-2E8751135CE4',
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.listRepRecoveryCdpRange(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listRepRecoveryCdpRange', body)

    def testListRepRecoveryCdpLog(self):
        a = Auth(username, pwd)
        body = {
            'rep_uuid': '051E0501-04EF-E1ED-0CEA-2E8751135CE4',
            'bk_path': '["G:\cdp2\G\cdp\"]',
            'expand_offset': '',
            'direction': '0',
            'cdp_time': '2019-01-08 01:20:54',
            'position': '',
            'bs_time': '2019-01-02_16-35-21',
            'baseline_page': 1,
        }
        repRecovery = RepRecovery(a)
        r = repRecovery.listRepRecoveryCdpLog(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listRepRecoveryCdpLog', body)

    def testViewRepRecoveryData(self):
        a = Auth(username, pwd)
        body = {
            'rep_recovery': {
            'cdp_position': '2017-11-17_15-30-40+-2',
            'rc_name': '',
            'cdp_time': '2018-04-24 13:43:26.0',
            'wk_uuid': 'Jane',
            'snapshot_size': '1.34 GB',
            'cdp_rc_method': 0,
            'snapshot_time': '2017-11-17 17:24:14',
            'rc_type': 0,
            'snapshot_name': 'c5809dd2-e8be-4389-ac0d-0a657ff94da0_snap_2017-11-17_17-24-14',
            'bk_path': [],
            'oph_policy': 0,
            'cdp_file': 'Baseline',
            'cdp_op': 'backup',
            'wk_path': [],
            'data_ip_uuid': 'd',
            'biz_grp_list': [],
            'bk_uuid': '',
            'bk_path_policy': '',
            'cdpShowOne': 'true',
            'cdpShowTwo': 'false',
            'compress': '0',
            'ct_name_str1': '',
            'ct_name_str2': '',
            'ct_name_type': '0',
            'data_path': '',
            'encrypt_switch': '0',
            'end_time': '',
            'isShowTime': '',
            'merge_path': '',
            'pointTime': '2020-10-19T06:57:59.399Z',
            'secret_key': '',
            'snapTable': [],
            'start_time': '',},
        }

        repRecovery = RepRecovery(a)
        r = repRecovery.viewRepRecoveryData(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'viewRepRecoveryData', body)

    def testListRcpRecoveryDataViewStatus(self):
        a = Auth(username, pwd)
        body = {
            'task_uuid': '',
            'node_uuid': '',
        }

        repRecovery = RepRecovery(a)
        r = repRecovery.listRcpRecoveryDataViewStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listRcpRecoveryDataViewStatus', body)

    def testListCDPRcData(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        repRecovery = RepRecovery(a)
        r = repRecovery.listCDPRcData(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'RepRecovery', 'listCDPRcData', body)


if __name__ == '__main__':
    unittest.main()  
