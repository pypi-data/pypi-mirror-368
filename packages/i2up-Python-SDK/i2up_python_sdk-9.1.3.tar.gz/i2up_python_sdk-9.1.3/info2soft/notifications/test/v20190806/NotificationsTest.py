
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.notifications.v20181227.Notifications import Notifications
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
    
                
class NotificationsTestCase(unittest.TestCase):

    def testAddNotifications(self):
        a = Auth(username, pwd)
        body = {
            'type': 'timing',
            'uuid': '82275AFD-97D0-15B4-D477-011E397113D6',
            'msg': '规则/任务执行失败/成功/超时/策略取消',
            'name': 'timing_test',
            'table': '',
            'module': '',
        }
        notifications = Notifications(a)
        r = notifications.addNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'addNotifications', body)

    def testTestNotificationsSms(self):
        a = Auth(username, pwd)
        body = {
            'temp_id': '',
            'mobile': '',
        }
        notifications = Notifications(a)
        r = notifications.testNotificationsSms(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'testNotificationsSms', body)


if __name__ == '__main__':
    unittest.main()  
