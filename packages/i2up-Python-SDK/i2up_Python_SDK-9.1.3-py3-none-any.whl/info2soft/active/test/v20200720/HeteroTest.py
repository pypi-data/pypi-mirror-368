
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.active.v20200720.Hetero import Hetero
# from info2soft.active.v20200722.Hetero import Hetero
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


class HeteroTestCase(unittest.TestCase):

    def testCreateHeteroRule(self):
        a = Auth(username, pwd)
        body = {
            'name': '',
            'kfk_ver': '',
            'dst_node': '',
            'conn_type': '',
            'host': '',
            'port': '',
            'broker': '',
            'tabmap': {},
            'consumer_thread_num': 2,
            'actload_thread_num': 4,
        }
        
        hetero = Hetero(a)
        r = hetero.createHeteroRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'createHeteroRule', body)

    def testDeleteHeteroRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        hetero = Hetero(a)
        r = hetero.deleteHeteroRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'deleteHeteroRule', body)

    def testListHeteroRule(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': 'kafka_name',
            'search_value': '',
        }
        
        hetero = Hetero(a)
        r = hetero.listHeteroRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listHeteroRule', body)

    def testCreateHeteroTopic(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.createHeteroTopic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'createHeteroTopic', body)

    def testCreateConsumer(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.createConsumer(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'createConsumer', body)

    def testConsumer(self):
        a = Auth(username, pwd)
        body = {
            'topic': '',
            'offset': '',
            'lines': '',
            'show_foward': 1,
        }
        
        hetero = Hetero(a)
        r = hetero.consumer(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'consumer', body)

    def testCreateConsumerRule(self):
        a = Auth(username, pwd)
        body = {
            'name': '',
            'src_db_uuid': '',
            'tgt_type': '',
            'init_offset': [{
            'topic': '',
            'offset': '',
            'partition': '',},],
            'modify': 'false',
            'topic': '',
            'dst_topic': '',
            'tgt_db_uuid': '',
            'init_offset_type': 'earlist',
            'tabmap': '{111:222}',
            'consumer_thread_num': '2',
            'actload_thread_num': '4',
            'kudu_partition_config': [],
            'impala_connected': '',
            'config': {
            'goldendb_config': {
            'machine_number': 1,
            'distribute_type': '',},
            'insert_date_config': {},
            'primary_key_config': {},},
        }
        
        hetero = Hetero(a)
        r = hetero.createConsumerRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'createConsumerRule', body)

    def testModifyConsumerRule(self):
        a = Auth(username, pwd)
        body = {
            'init_offset_type': 'earlist',
            'modify': 'false',
            'tabmap': '{111:222}',
            'consumer_thread_num': '2',
            'actload_thread_num': '4',
            'tgt_db_uuid': '',
            'name': '',
            'src_db_uuid': '',
            'tgt_type': '',
            'init_offset': [{
            'topic': '',
            'offset': '',
            'partition': '',},],
            'topic': '',
            'dst_topic': '',
            'uuid': '@guuid',
            'user_uuid': '@guuid',
        }
        
        hetero = Hetero(a)
        r = hetero.modifyConsumerRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'modifyConsumerRule', body)

    def testDeleteConsumerRules(self):
        a = Auth(username, pwd)
        body = {
            'uuid': [],
            'force': 1,
        }
        
        hetero = Hetero(a)
        r = hetero.deleteConsumerRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'deleteConsumerRules', body)

    def testListConsumerStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        hetero = Hetero(a)
        r = hetero.listConsumerStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listConsumerStatus', body)

    def testStopConsumerRule(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'operate': 'stop',
        }

        hetero = Hetero(a)
        r = hetero.stopConsumerRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'stopConsumerRule', body)

    def testResumeConsumerRule(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'operate': 'resume',
        }

        hetero = Hetero(a)
        r = hetero.resumeConsumerRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'resumeConsumerRule', body)

    def testListConsumerRules(self):
        a = Auth(username, pwd)
        body = {
            'search_field': 'tgt_type',
            'limit': 1,
            'page': 1,
            'search_value': '',
            'where_args': {
            'uuid': '',},
        }
        
        hetero = Hetero(a)
        r = hetero.listConsumerRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listConsumerRules', body)

    def testDescribeConsumerRules(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.describeConsumerRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'describeConsumerRules', body)

    def testCreateHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'graph_name': '',
            'is_parent': '',
            'is_rule': '',
            'consume_rule': [{
            'id': '',
            'rule_number': 1,
            'rule_name': '',
            'src_type': '',
            'src_uuid': '',
            'dst_type': '',
            'dst_uuid': '',
            'rule_status': '',
            'is_parent': '',
            'is_rule': '',
            'src_name': '',
            'dst_name': '',
            'rule_traffic': '',},],
        }
        
        hetero = Hetero(a)
        r = hetero.createHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'createHeteroGraph', body)

    def testAddHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'graph_uuid': '',
            'rule_number': '',
            'src_type': '',
            'rule_uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.addHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'addHeteroGraph', body)

    def testListHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
        }
        
        hetero = Hetero(a)
        r = hetero.listHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listHeteroGraph', body)

    def testRunHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'graphs': [],
            'graph_uuid': '',
            'rule_uuids': [{
            'uuid': '',
            'src_type': '',},],
        }
        
        hetero = Hetero(a)
        r = hetero.runHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'runHeteroGraph', body)

    def testStopHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'graphs': [{
            'graph_uuid': '',
            'rule_uuids': [{
            'uuid': '',
            'src_type': '',},],},],
        }
        
        hetero = Hetero(a)
        r = hetero.stopHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'stopHeteroGraph', body)

    def testListGraphStatus(self):
        a = Auth(username, pwd)
        body = {
            'rule_uuids': [{
                'uuid': '',
                'src_type': '', }, ],
        }
        
        hetero = Hetero(a)
        r = hetero.listGraphStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listGraphStatus', body)

    def testDeleteHeteroGraph(self):
        a = Auth(username, pwd)
        body = {
            'graph_uuids': [{
            'graph_uuid': 'CcB11Bf6-1D15-dcF4-Ed71-60c7d3CBeDcA',
            'rule_uuids': [{
            'uuid': '86d28b2c-b6E1-2c1F-3F0D-ECbfB5dE3A50',
            'is_rule': '1',
            'rule_number': '4',
            'src_type': 'oracle',},],},],
            'is_whole': '1',
        }
        
        hetero = Hetero(a)
        r = hetero.deleteHeteroGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'deleteHeteroGraph', body)

    def testDescriptGraphDetail(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'start_time': '',
            'end_time': '',
            'graph_uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.descriptGraphDetail(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'descriptGraphDetail', body)

    def testListGraph(self):
        a = Auth(username, pwd)
        body = {
            'graph_uuid': '',
        }
        
        hetero = Hetero(a)
        r = hetero.listGraph(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Hetero', 'listGraph', body)


if __name__ == '__main__':
    unittest.main()
