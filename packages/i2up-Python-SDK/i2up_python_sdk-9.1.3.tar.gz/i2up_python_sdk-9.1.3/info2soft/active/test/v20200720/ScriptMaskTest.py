
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'/Users/chengl/Desktop/sdk/python-sdk/')

import unittest
from info2soft.active.v20200720.ScriptMask import ScriptMask
# from info2soft.active.v20200722.ScriptMask import ScriptMask
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
    
                
class ScriptMaskTestCase(unittest.TestCase):

    def testCreateScript(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'node_uuid': '',
            'config': {
            'script': [],
            'src_type': '',
            'dyn_thd': 1,
            'lderrset': 'continue',
            'policy': {
            'policy_type': 'immediate',
            'one_time': '',
            'time_policy': '',},},
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.createScript(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'createScript', body)

    def testDeleteScript(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.deleteScript(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'deleteScript', body)

    def testModifyScript(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'rule_uuid': '',
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'node_uuid': '',
            'config': {
            'script': [],
            'src_type': '',
            'dyn_thd': 1,
            'lderrset': 'continue',
            'policy': {
            'policy_type': 'immediate',
            'one_time': '',
            'time_policy': '',},},
        }

        scriptMask = ScriptMask(a)
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        r = scriptMask.modifyScript(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'modifyScript', body)

    def testListScript(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'limit': 10,
            'search_field': '',
            'search_value': '',
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.listScript(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'listScript', body)

    def testDescriptScript(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        scriptMask = ScriptMask(a)
        r = scriptMask.descriptScript(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'descriptScript', body)

    def testCreateRule(self):
        a = Auth(username, pwd)
        body = {
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'node_uuid': '',
            'config': {
            'script': [],
            'src_type': '',
            'dyn_thd': 1,
            'lderrset': 'continue',
            'policy': {
            'policy_type': 'immediate',
            'one_time': '',
            'time_policy': '',},},
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.createRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'createRule', body)

    def testDeleteRule(self):
        a = Auth(username, pwd)
        body = {
            'uuids': '',
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.deleteRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'deleteRule', body)

    def testModifyDb(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'rule_uuid': '',
            'rule_name': '',
            'src_db_uuid': '',
            'tgt_db_uuid': '',
            'node_uuid': '',
            'config': {},
            'script': [],
            'src_type': '',
            'dyn_thd': 1,
            'lderrset': 'continue',
            'policy': {},
            'policy_type': 'immediate',
            'one_time': '',
            'time_policy': '',
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.modifyDb(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'modifyDb', body)

    def testListRules(self):
        a = Auth(username, pwd)
        body = {
            'limit': 10,
            'page': 1,
            'search_field': 'rule_name',
            'search_value': '',
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.listRules(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'listRules', body)

    def testDescriptRule(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        scriptMask = ScriptMask(a)
        r = scriptMask.descriptRule(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'descriptRule', body)

    def testListRuleStatus(self):
        a = Auth(username, pwd)
        body = {
            'uuids': [],
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.listRuleStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'listRuleStatus', body)

    def testStartRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'uuids': [],
        }
        
        scriptMask = ScriptMask(a)
        r = scriptMask.startRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'startRule', body)

    def testStopRule(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'stop',
            'uuids': [],
        }

        scriptMask = ScriptMask(a)
        r = scriptMask.stopRule(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ScriptMask', 'stopRule', body)


if __name__ == '__main__':
    unittest.main()
