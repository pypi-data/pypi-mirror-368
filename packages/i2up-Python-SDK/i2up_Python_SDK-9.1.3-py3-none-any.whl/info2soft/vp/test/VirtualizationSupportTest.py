# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.vp.VirtualizationSupport import VirtualizationSupport
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


class VirtualizationSupportTestCase(unittest.TestCase):

    def testDescribeVpRuleRate(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'wk_uuid': 'F28BA5A6-4FF9-E596-4371-1ED203D45143',
            'mode': 'month',
            'type': 'I2VP_BK',
            'group_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpRuleRate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpRuleRate', body)

    def testDescribeVmProtectRate(self):
        a = Auth(username, pwd)
        body = {
            'vp_uuid': 'F28BA5A6-4FF9-E596-4371-1ED203D45143',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVmProtectRate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVmProtectRate', body)

    def testCreateVpBackup(self):
        a = Auth(username, pwd)
        body = {
            'del_bkup_data': 0,
            'quiet_snap': 0,
            'quick_back': 1,
            'vp_uuid': 'C6335F62-2565-1957-4BB9-587F2FF46B00',
            'bk_path': 'E:\\vp_bk5\\',
            'vm_list': [{
                'vm_name': '测试5',
                'vm_ref': 'vm-10811',
                'scripts_type': 1,
                'scripts': '',
                'new_vm_name': '虚机名称_2020-04-29',
                'cpu': '',
                'core_per_sock': '',
                'mem_mb': '',
                'os_type': 1,
                'disk_list': [{
                    'id': '',
                    'disk_path': '',
                    'disk_name': '',
                    'is_ignored': 1, }, ], }, ],
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'lan_free': 23,
            'rule_name': 'vp_bk cky',
            'bkup_policy': 1,
            'bkup_one_time': 1546831899,
            'bkup_schedule': [{
                'limit': 3,
                'sched_day': [
                    '1',
                    '2',
                    '3', ],
                'sched_time': [
                    '00:00', ],
                'sched_every': 0,
                'bkup_type': 0, }, ],
            'biz_grp_list': [],
            'rule_type': 0,
            'band_width': '-1',
            'compress': 0,
            'mem_snap': 0,
            'random_str': '11111111-1111-1111-1111-111111111111',
            'instant_recovery': 1,
            'auto': 0,
            'add_drill': 1,
            'drill_plat_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpBackup', body)

    def testModifyVpBackup(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVpBackup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVpBackup', body)

    def testDescribeVpBackup(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpBackup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpBackup', body)

    def testDescribeVpBackupGroup(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpBackupGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpBackupGroup', body)

    def testListVpBackup(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'type': 0,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpBackup', body)

    def testListVpBackupGroup(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'type': 0,
            'where_args[bk_path]': 'H:\\vp_bk5\\',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpBackupGroup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpBackupGroup', body)

    def testListVpBackupStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpBackupStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpBackupStatus', body)

    def testStartVpBackup(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '[C6335F62-2565-1957-4BB9-587F2FF46B00]',
            'group_uuids': [],
            'bkup_type': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpBackup', body)

    def testStoptVpBackup(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'rule_uuids': '[C6335F62-2565-1957-4BB9-587F2FF46B00]',
            'group_uuids': [],
            'bkup_type': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpBackup', body)

    def testDeleteVpBackup(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
            'group_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpBackup(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpBackup', body)

    def testDeleteVpBackupPoint(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'version_list': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpBackupPoint(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpBackupPoint', body)

    def testCreateVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'bk_path_view': 'H:\vp_bk5\testRC1_BAK_99_192.168.85.139',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'new_ds': 'datastore1',
            'vm_list': [{
                'ver_sig': 'A59DB76E-E33D-4E22-BB08-59723B1FC539',
                'vm_ref': '99',
                'vm_name': '测试5',
                'disk_list': [{
                    'disk_name': 'proxy gateway1.vmdk',
                    'disk_path': '/',
                    'is_same': 1,
                    'new_ds': 'datastore1',
                    'id': '',
                    'boot_index': 1, }, ],
                'new_vm_name': '测试5',
                'networks': [{
                    'keep_mac': 1,
                    'network_name': '',
                    'network_id': '',
                    'source_network_name': '',
                    'source_network_id': '',
                    'source_mac_address': '', }, ],
                'bk_path': '',
                'ver_time': '',
                'cpu': 1,
                'core_per_sock': 1,
                'mem_mb': 1,
                'dynamic_mem': 1,
                'flavor_id': '', }, ],
            'new_hostname': 'localhost.localdomain',
            'new_dc': 'ha-datacenter',
            'is_create': 0,
            'vp_uuid': '928B88A6-CDBA-6F55-ADCB-15A8A935C9C2',
            'new_ds_path': '/',
            'new_vp_uuid': '928B88A6-CDBA-6F55-ADCB-15A8A935C9C2',
            'rule_name': 'testRC cky',
            'lan_free': 23,
            'rule_type': 0,
            'auto_startup': 0,
            'new_dc_mor': 'ha-datacenter',
            'api_type': 'HostAgent',
            'biz_grp_list': [],
            'group_recovery': 0,
            'backup_rule_name': 'testRC1',
            'band_width': '-1',
            'for_vp_file_rc': 1,
            'del_vm': 1,
            'network_id': '',
            'network_name': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpRecovery', body)

    def testDescribeVpRecoveryGroup(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpRecoveryGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpRecoveryGroup', body)

    def testListVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'type': 0,
            'limit': 10,
            'page': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpRecovery', body)

    def testListVpRecoveryStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpRecoveryStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpRecoveryStatus', body)

    def testStartVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '641A27BB-B4D1-F482-1FB8-E856898626DA',
            'rule_type': 0,
            'group_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpRecovery', body)

    def testStopVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'rule_uuids': '641A27BB-B4D1-F482-1FB8-E856898626DA',
            'rule_type': 0,
            'group_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpRecovery', body)

    def testClearFinishVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '641A27BB-B4D1-F482-1FB8-E856898626DA',
            'rule_type': 0,
            'group_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.clearFinishVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'clearFinishVpRecovery', body)

    def testDeleteVpRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
            'group_uuids': [],
            'delete_tgtvm': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpRecovery', body)

    def testCreateVpMove(self):
        a = Auth(username, pwd)
        body = {
            'new_ds': '103-数据盘',
            'tgt_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'src_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'automate': 0,
            'rule_name': 'testMove1 cky',
            'new_dc': 'i2test',
            'bk_path': 'H:\\vp_rep\\',
            'backup_type': 'i',
            'new_host': '192.168.88.103',
            'quiet_snap': 1,
            'bkup_schedule': {
                'sched_time_start': '0',
                'limit': 0,
                'sched_day': 25,
                'sched_every': 0,
                'sched_time': [],
                'sched_gap_min': 0, },
            'quick_back': 1,
            'lan_free': 23,
            'vm_list': [{
                'vm_name': '新建虚拟机1',
                'vm_ref': 'vm-11877',
                'shd_name': '新建虚拟机1_move',
                'disk_list': [{
                    'disk_path': '',
                    'disk_name': '[datastore1 (1)] 测试11_临时测试11/测试11_临时测试11_5-000002.vmdk',
                    'new_ds': 'datastore2',
                    'id': '',
                    'is_ignored': 1,
                    'boot_index': 1, }, ],
                'scripts_type': '',
                'scripts': '',
                'cpu': '',
                'core_per_sock': '',
                'mem_mb': '',
                'os_type': 1,
                'new_vm_name': '',
                'dynamic_mem': 1,
                'networks': [{
                    'network_id': '',
                    'network_name': '',
                    'keep_mac': 1,
                    'source_network_name': '',
                    'source_network_id': '',
                    'mac_address': '', }, ],
                'flavor_id': '', }, ],
            'new_dc_mor': 'datacenter-2',
            'bkup_policy': 0,
            'band_width': '-1',
            'rule_type': 1,
            'auto_shutdown': 1,
            'auto_startup': '',
            'biz_grp_list': [],
            'auto': '',
            'add_drill': 1,
            'drill_plat_uuid': '',
            'mem_snap': 1,
            'overwrite': 1,
            'network_id': '',
            'network_name': '',
            'agent_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpMove', body)

    def testCreateVpRep(self):
        a = Auth(username, pwd)
        body = {
            'new_ds': '103-数据盘',
            'tgt_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'src_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'automate': 0,
            'rule_name': 'testMove1 cky',
            'new_dc': 'i2test',
            'bk_path': 'H:\\vp_rep\\',
            'backup_type': 'i',
            'new_host': '192.168.88.103',
            'quiet_snap': 1,
            'bkup_schedule': {
                'sched_time_start': '0',
                'limit': 0,
                'sched_day': 25,
                'sched_every': 0,
                'sched_time': [],
                'sched_gap_min': 0, },
            'quick_back': 1,
            'lan_free': 23,
            'vm_list': [{
                'vm_name': '新建虚拟机1',
                'vm_ref': 'vm-11877',
                'shd_name': '新建虚拟机1_move',
                'disk_list': [{
                    'disk_path': '',
                    'disk_name': '[datastore1 (1)] 测试11_临时测试11/测试11_临时测试11_5-000002.vmdk',
                    'new_ds': 'datastore2',
                    'id': '',
                    'is_ignored': 1,
                    'boot_index': 1, }, ],
                'scripts_type': '',
                'scripts': '',
                'cpu': '',
                'core_per_sock': '',
                'mem_mb': '',
                'os_type': 1,
                'new_vm_name': '',
                'dynamic_mem': 1,
                'networks': [{
                    'network_id': '',
                    'network_name': '',
                    'keep_mac': 1,
                    'source_network_name': '',
                    'source_network_id': '',
                    'mac_address': '', }, ],
                'flavor_id': '', }, ],
            'new_dc_mor': 'datacenter-2',
            'bkup_policy': 0,
            'band_width': '-1',
            'rule_type': 1,
            'auto_shutdown': 1,
            'auto_startup': '',
            'biz_grp_list': [],
            'auto': '',
            'add_drill': 1,
            'drill_plat_uuid': '',
            'mem_snap': 1,
            'overwrite': 1,
            'network_id': '',
            'network_name': '',
            'agent_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpRep', body)

    def testBatchCreateVpRep(self):
        a = Auth(username, pwd)
        body = {
            'vm_list': [{
                'vm_name': '新建虚拟机1',
                'vm_ref': 'vm-11877',
                'shd_name': '新建虚拟机1_move',
                'disk_list': [{
                    'disk_path': '',
                    'disk_name': '[datastore1 (1)] 测试11_临时测试11/测试11_临时测试11_5-000002.vmdk',
                    'new_ds': 'datastore2',
                    'id': '',
                    'is_ignored': 1, }, ],
                'scripts_type': '',
                'scripts': '',
                'cpu': '',
                'core_per_sock': '',
                'mem_mb': '',
                'os_type': 1,
                'new_vm_name': '',
                'dynamic_mem': 1,
                'networks': [{
                    'network_id': '',
                    'network_name': '',
                    'keep_mac': 1,
                    'source_network_name': '',
                    'source_network_id': '',
                    'mac_address': '', }, ],
                'bk_uuid': '',
                'bk_path': '',
                'add_drill': 1,
                'auto': 1,
                'vm_uuid': '', }, ],
            'base_info_list': {
                'rule_type': 0,
                'biz_grp_list': '',
                'quick_back': 1,
                'quiet_snap': 1,
                'lan_free': 23,
                'mem_snap': 1,
                'band_width': '-1',
                'auto_shutdown': 1,
                'auto_startup': 0,
                'overwrite': 1,
                'bkup_schedule': {
                    'sched_time_start': '',
                    'limit': 1,
                    'sched_day': '',
                    'sched_every': 1,
                    'sched_time': [],
                    'sched_gap_min': 0, },
                'bkup_policy': 1,
                'backup_type': 'i',
                'automate': 0,
                'tgt_uuid': '',
                'new_dc': '',
                'new_dc_mor': '',
                'new_host': '',
                'new_ds': '',
                'network_id': '',
                'network_name': '', },
            'common_params': {
                'batch_name': '',
                'rep_prefix': '',
                'rep_sufix': '',
                'variable_type': 1, },
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.batchCreateVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'batchCreateVpRep', body)

    def testModifyVpRepGroup(self):
        a = Auth(username, pwd)
        body = {
            'new_ds': '103-数据盘',
            'support_cbt': 1,
            'tgt_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'del_bkup_swap': 0,
            'src_uuid': '7F16E670-1A61-D565-6905-9C68B9520907',
            'bk_uuid': '67E33CDB-D75B-15B3-367D-50C764F5A26F',
            'automate': 0,
            'rule_name': 'testMove1 cky',
            'new_dc': 'i2test',
            'bk_path': 'H:\\vp_rep\\',
            'backup_type': 'i',
            'new_host': '192.168.88.103',
            'quiet_snap': 1,
            'bkup_schedule': {
                'sched_time_start': '0',
                'limit': 0,
                'sched_day': 21,
                'sched_every': 0,
                'sched_time': [],
                'sched_gap_min': 0, },
            'quick_back': 1,
            'del_bkup_data': 0,
            'lan_free': 23,
            'vm_list': [{
                'vm_name': '新建虚拟机1',
                'vm_ref': 'vm-11877',
                'shd_name': '新建虚拟机1_move',
                'overwrite': 0,
                'disk_list': [{
                    'disk_path': '',
                    'disk_name': '[datastore1 (1)] 测试11_临时测试11/测试11_临时测试11_5-000002.vmdk',
                    'new_ds': 'datastore2',
                    'id': '', }, ], }, ],
            'time_window': '',
            'new_dc_mor': 'datacenter-2',
            'bkup_policy': 0,
            'band_width': '-1',
            'rule_type': 1,
            'auto_shutdown': 1,
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVpRepGroup(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVpRepGroup', body)

    def testDescribeVpMove(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpMove(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpMove', body)

    def testDescribeVpRep(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpRep(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpRep', body)

    def testModifyVpMove(self):
        a = Auth(username, pwd)
        body = {
            'new_ds': '',
            'support_cbt': 1,
            'tgt_uuid': '',
            'del_bkup_swap': 1,
            'src_uuid': '3D0BDA2c-5B5F-f2f8-bc49-aBdD8cb2BCF8',
            'bk_uuid': '',
            'automate': 1,
            'rule_name': '',
            'new_dc': '',
            'bk_path': '',
            'backup_type': '',
            'new_host': '',
            'quiet_snap': 1,
            'bkup_schedule': {},
            'quick_back': 1,
            'del_bkup_data': 1,
            'lan_free': 1,
            'vm_list': [],
            'time_window': '',
            'new_dc_mor': '',
            'bkup_policy': 1,
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVpMove(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVpMove', body)

    def testModifyVpRep(self):
        a = Auth(username, pwd)
        body = {
            'new_ds': '',
            'support_cbt': 1,
            'tgt_uuid': '',
            'del_bkup_swap': 1,
            'src_uuid': '3D0BDA2c-5B5F-f2f8-bc49-aBdD8cb2BCF8',
            'bk_uuid': '',
            'automate': 1,
            'rule_name': '',
            'new_dc': '',
            'bk_path': '',
            'backup_type': '',
            'new_host': '',
            'quiet_snap': 1,
            'bkup_schedule': {},
            'quick_back': 1,
            'del_bkup_data': 1,
            'lan_free': 1,
            'vm_list': [],
            'time_window': '',
            'new_dc_mor': '',
            'bkup_policy': 1,
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVpRep(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVpRep', body)

    def testListVpMove(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpMove', body)

    def testListVpRep(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpRep', body)

    def testListVpMoveStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpMoveStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpMoveStatus', body)

    def testListVpRepStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpRepStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpRepStatus', body)

    def testStopVpMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpMove', body)

    def testStartVpMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpMove', body)

    def testMoveVpMove(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.moveVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'moveVpMove', body)

    def testStopVpRep(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpRep', body)

    def testStartVpRep(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpRep', body)

    def testFailoverVpRep(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.failoverVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'failoverVpRep', body)

    def testFailbackVpRep(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.failbackVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'failbackVpRep', body)

    def testCreateTargeVm(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'start',
            'rule_uuids': '1C89A121-6B03-24B2-9273-D4B93C0687AD',
            'snap_point': '',
            'op_code': '',
            'group_uuids': [],
            'power_on': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createTargeVm(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createTargeVm', body)

    def testDeleteVpMove(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
            'group_uuids': [],
            'delete_tgtvm': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpMove(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpMove', body)

    def testDeleteVpRep(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
            'group_uuids': [],
            'delete_tgtvm': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpRep(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpRep', body)

    def testListVpRepPointList(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpRepPointList(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpRepPointList', body)

    def testListVpMovePointList(self):
        a = Auth(username, pwd)
        body = {
            'type': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpMovePointList(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpMovePointList', body)

    def testDescribeVpFileRecoveryVmIp(self):
        a = Auth(username, pwd)
        body = {
            'recovery_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpFileRecoveryVmIp(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpFileRecoveryVmIp', body)

    def testVpFileRecoveryLivecdPartition(self):
        a = Auth(username, pwd)
        body = {
            'recovery_uuid': 'E16C82aF-7DBC-A12F-8DdA-fEE3B6eD5f44',
            'bk_ip': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.vpFileRecoveryLivecdPartition(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'vpFileRecoveryLivecdPartition', body)

    def testCreateVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'wk_ip': '',
            'os_user': '',
            'os_pwd': '',
            'wk_port': 26888,
            'wk_path': [],
            'is_override': 0,
            'rule_name': '',
            'recovery_uuid': '',
            'bk_path': [],
            'bk_ip': '',
            'is_remote': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpFileRecovery', body)

    def testModifyVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
            'rule_name': '',
            'config_addr': '',
            'config_port': '',
            'attach_dir': '',
            'bk_uuid': '',
            'bk_path': '',
            'vm_name': '',
            'version_id': '',
            'tgt_uuid': '',
            'random_str': '',
            'attach_path': '',
            'tgt_path': '',
            'files': [],
            'version_time': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.modifyVpFileRecovery(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'modifyVpFileRecovery', body)

    def testDescribeVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpFileRecovery(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpFileRecovery', body)

    def testListVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 1,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpFileRecovery', body)

    def testAttachVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.attachVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'attachVpFileRecovery', body)

    def testDetachVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.detachVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'detachVpFileRecovery', body)

    def testStartVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpFileRecovery', body)

    def testStopVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpFileRecovery', body)

    def testListVpFileRecoveryStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpFileRecoveryStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpFileRecoveryStatus', body)

    def testDeleteVpFileRecovery(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpFileRecovery(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpFileRecovery', body)

    def testListVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpDrill', body)

    def testCreateVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'rule_type': 0,
            'vp_uuid': '',
            'auto': 0,
            'vm_list': [{
                'vm_name': '',
                'new_vm_name': '',
                'vm_ref': '99',
                'cpu': 1,
                'ver_sig': '',
                'core_per_sock': 1,
                'mem_mb': 1024,
                'scripts': '',
                'bk_uuid': '',
                'bk_path': '',
                'time': '',
                'original_rule_uuid': '',
                'scripts_type': 1,
                'os_type': 1,
                'wk_uuid': '',
                'src_uuid': '', }, ],
            'quick_back': 1,
            'backup_type': 'i',
            'lan_free': 23,
            'del_bkup_data': 0,
            'automate': 0,
            'auto_shutdown': 1,
            'bkup_policy': 0,
            'bkup_schedule': {
                'sched_time_start': '0',
                'limit': 0,
                'sched_day': 6,
                'sched_every': 0,
                'sched_time': [],
                'sched_gap_min': 0, },
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.createVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'createVpDrill', body)

    def testDescribeVpDrill(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.describeVpDrill(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'describeVpDrill', body)

    def testDeleteVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
            'group_uuids': [],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.deleteVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'deleteVpDrill', body)

    def testListVpDrillStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [
                '11111111-1111-1111-1111-111111111111', ],
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.listVpDrillStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'listVpDrillStatus', body)

    def testGetConsoleUrl(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuid': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.getConsoleUrl(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'getConsoleUrl', body)

    def testStopVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '[C6335F62-2565-1957-4BB9-587F2FF46B00]',
            'group_uuids': [],
            'status': '',
            'msg': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.stopVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'stopVpDrill', body)

    def testStartVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '[C6335F62-2565-1957-4BB9-587F2FF46B00]',
            'group_uuids': [],
            'status': '',
            'msg': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.startVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'startVpDrill', body)

    def testSetStatusVpDrill(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'rule_uuids': '[C6335F62-2565-1957-4BB9-587F2FF46B00]',
            'group_uuids': [],
            'status': '',
            'msg': '',
        }

        virtualizationSupport = VirtualizationSupport(a)
        r = virtualizationSupport.setStatusVpDrill(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'VirtualizationSupport', 'setStatusVpDrill', body)


if __name__ == '__main__':
    unittest.main()
