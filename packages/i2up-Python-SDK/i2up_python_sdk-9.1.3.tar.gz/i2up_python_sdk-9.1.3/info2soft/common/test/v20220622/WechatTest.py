
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.common.Wechat import Wechat
# from info2soft.common.v20200722.Wechat import Wechat
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


class WechatTestCase(unittest.TestCase):

    def testBindUser(self):
        a = Auth(username, pwd)
        body = {
            'token': '',
            'from': '',
        }
        
        wechat = Wechat(a)
        r = wechat.bindUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Wechat', 'bindUser', body)

    def testUnbindUser(self):
        a = Auth(username, pwd)
        body = {
        }
        
        wechat = Wechat(a)
        r = wechat.unbindUser(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Wechat', 'unbindUser', body)

    def testBindStatus(self):
        a = Auth(username, pwd)
        body = {
        }
        
        wechat = Wechat(a)
        r = wechat.bindStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Wechat', 'bindStatus', body)


if __name__ == '__main__':
    unittest.main()
