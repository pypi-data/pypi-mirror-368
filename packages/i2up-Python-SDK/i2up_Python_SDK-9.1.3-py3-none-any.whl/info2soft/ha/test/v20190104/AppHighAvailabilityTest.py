# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.ha.v20181227.AppHighAvailability import AppHighAvailability
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


class AppHighAvailabilityTestCase(unittest.TestCase):

    def testListHA(self):
        a = Auth(username, pwd)
        body = {
            'filter_value': '',
            'filter_type': '',
            'page': '1',
            'limit': '10',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listHA', body)

    def testStartHA(self):
        a = Auth(username, pwd)
        body = {
            'ha_uuid': ['11111111-1111-1111-1111-111111111111'],
            'node_uuid': '11111111-1111-1111-1111-111111111111',
            'type': 'start',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.startHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'startHA', body)

    def testStopHA(self):
        a = Auth(username, pwd)
        body = {
            'ha_uuid': ['11111111-1111-1111-1111-111111111111'],
            'node_uuid': '11111111-1111-1111-1111-111111111111',
            'type': 'stop',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.stopHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'stopHA', body)

    def testForceSwitchHA(self):
        a = Auth(username, pwd)
        body = {
            'ha_uuid': ['11111111-1111-1111-1111-111111111111'],
            'node_uuid': '11111111-1111-1111-1111-111111111111',
            'type': 'force_switch',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.forceSwitchHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'forceSwitchHA', body)

    def testDeleteHA(self):
        a = Auth(username, pwd)
        body = {
            'uuid': ['11111111-1111-1111-1111-111111111111', ],
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.deleteHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'deleteHA', body)

    def testListHAStatus(self):
        a = Auth(username, pwd)
        body = {
            'ha_uuid': ['11111111-1111-1111-1111-111111111111', ],
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listHAStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listHAStatus', body)

    def testDescribeHAScriptPath(self):
        a = Auth(username, pwd)
        body = {
            'master_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.describeHAScriptPath(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'describeHAScriptPath', body)

    def testListNicInfo(self):
        a = Auth(username, pwd)
        body = {
            'node_uuid': ['B8566905-411E-B2CD-A742-77B1346D8E84', '67E33CDB-D75B-15B3-367D-50C764F5A26F', ],
            'master_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.listNicInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'listNicInfo', body)

    def testCreateHA(self):
        a = Auth(username, pwd)
        body = {
            'heartbeat': [
                {
                    'interval': 2,
                    'maxfail': 5,
                    'protocol': 'tcp',
                    'ifconfig': [
                        {
                            'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                            'netif': '{AB1E4EFF-14FE-441E-8A1F-EE59BDA12D6F}',
                            'ip': '192.168.72.75',
                        }, {
                            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                            'netif': '{5C3A44A0-EF11-4705-A9A3-2F3ACEED4798}',
                            'ip': '192.168.72.82',
                        }
                    ],
                    'port': 26850,
                },
            ],
            'sync_data': [
                {
                    'back_rule': 0,
                    'need_rep_status': 1,
                    'create_start': 0,
                    'wait_cache': 1,
                    'rule_relation': [
                        {

                            'rep_name': 'sdk_ha-N3_72.75-N4_72.76',
                            'autostart_rep': 0,
                            'path': ['E:\\test\\', ],
                            'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                            'append_name': 0,
                        },
                        {
                            'rep_name': 'sdk_ha-N3_72.75-N4_72.76',
                            'autostart_rep': 0,
                            'path': ['E:\\test\\', ],
                            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                            'append_name': 0,
                        }],
                    'excludes': [],
                }],
            'arbitration': {
                'radio': 1,
                'node': {
                    'arbit_protocol': 'TCP',
                    'arbit_addr': '192.168.72.82',
                    'arbit_port': 26868,
                },
                'disk': {'path': ''},
            },
            'master_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'ha_name': 'sdk_ha',
            'res_switch': [
                {
                    'script': {
                        'after_failover': '',
                        'before_failover': '',
                        'before_switch': '',
                        'after_switch': '',
                    },
                    'vip': {
                        'top': 0,
                        'ip': '192.168.72.82',
                        'ifconfig': [
                            {
                                'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                                'netif': '{AB1E4EFF-14FE-441E-8A1F-EE59BDA12D6F}',
                                'label': 'Ethernet0',
                            },
                            {

                                'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                                'netif': '{5C3A44A0-EF11-4705-A9A3-2F3ACEED4798}',
                                'label': 'Ethernet0',
                            }],
                        'mask': '255.255.255.0',
                        'del': 0,
                    },
                    'type': 'ip',
                }, ],
            'auto_switch': 1,
            'monitor': [
                {
                    'threshold': 90,
                    'interval': 2,
                    'name': '',
                    'script': '',
                    'access_method': '',
                    'type': 'cpu',
                    'great': '',
                    'useid': '',
                    'maxfail': 5,
                    'action': 'warn',
                    'residual': 1,
                    'role': 'master',
                    'path': '',
                    'monitor_file': '',
                }],
            'node_priority': [
                {
                    'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                    'priority': 'high',
                },
                {
                    'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                    'priority': 'high',
                }, ],
            'ctrl_switch': 0,
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.createHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'createHA', body)

    def testModifyHA(self):
        a = Auth(username, pwd)
        body = {
            'heartbeat': [
                {
                    'interval': 2,
                    'maxfail': 5,
                    'protocol': 'tcp',
                    'ifconfig': [
                        {
                            'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                            'netif': '{AB1E4EFF-14FE-441E-8A1F-EE59BDA12D6F}',
                            'ip': '192.168.72.75',
                        }, {
                            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                            'netif': '{5C3A44A0-EF11-4705-A9A3-2F3ACEED4798}',
                            'ip': '192.168.72.82',
                        }
                    ],
                    'port': 26850,
                },
            ],
            'sync_data': [
                {
                    'back_rule': 0,
                    'need_rep_status': 1,
                    'create_start': 0,
                    'wait_cache': 1,
                    'rule_relation': [
                        {

                            'rep_name': 'sdk_ha-N3_72.75-N4_72.76',
                            'autostart_rep': 0,
                            'path': ['E:\\test\\', ],
                            'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                            'append_name': 0,
                        },
                        {
                            'rep_name': 'sdk_ha-N3_72.75-N4_72.76',
                            'autostart_rep': 0,
                            'path': ['E:\\test\\', ],
                            'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                            'append_name': 0,
                        }],
                    'excludes': [],
                }],
            'arbitration': {
                'radio': 1,
                'node': {
                    'arbit_protocol': 'TCP',
                    'arbit_addr': '192.168.72.82',
                    'arbit_port': 26868,
                },
                'disk': {'path': ''},
            },
            'master_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'ha_name': 'sdk_ha',
            'res_switch': [
                {
                    'script': {
                        'after_failover': '',
                        'before_failover': '',
                        'before_switch': '',
                        'after_switch': '',
                    },
                    'vip': {
                        'top': 0,
                        'ip': '192.168.72.82',
                        'ifconfig': [
                            {
                                'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                                'netif': '{AB1E4EFF-14FE-441E-8A1F-EE59BDA12D6F}',
                                'label': 'Ethernet0',
                            },
                            {

                                'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                                'netif': '{5C3A44A0-EF11-4705-A9A3-2F3ACEED4798}',
                                'label': 'Ethernet0',
                            }],
                        'mask': '255.255.255.0',
                        'del': 0,
                    },
                    'type': 'ip',
                }, ],
            'auto_switch': 1,
            'monitor': [
                {
                    'threshold': 90,
                    'interval': 2,
                    'name': '',
                    'script': '',
                    'access_method': '',
                    'type': 'cpu',
                    'great': '',
                    'useid': '',
                    'maxfail': 5,
                    'action': 'warn',
                    'residual': 1,
                    'role': 'master',
                    'path': '',
                    'monitor_file': '',
                }],
            'node_priority': [
                {
                    'uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
                    'priority': 'high',
                },
                {
                    'uuid': 'B8566905-411E-B2CD-A742-77B1346D8E84',
                    'priority': 'high',
                }, ],
            'ctrl_switch': 1,
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.modifyHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'modifyHA', body)

    def testDescribeHA(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '11111111-1111-1111-1111-111111111111'
        }
        appHighAvailability = AppHighAvailability(a)
        r = appHighAvailability.describeHA(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'AppHighAvailability', 'describeHA', body)


if __name__ == '__main__':
    unittest.main()
