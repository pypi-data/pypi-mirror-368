
# -*- coding: utf-8 -*-
# flake8: noqa

import unittest
from info2soft.notifications.v20181227.Notifications import Notifications
from info2soft import Auth
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

    def testListNotifications(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.listNotifications(body)
        print(r[0])

    def testDescribeNotifications(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.describeNotifications(body)
        print(r[0])

    def testDescribeNotificationsCount(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.describeNotificationsCount(body)
        print(r[0])

    def testTempFuncName(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.tempFuncName(body)
        print(r[0])

    def testDescribeNotificationsConfig(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.describeNotificationsConfig(body)
        print(r[0])

    def testUpdateNotificationsConfig(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.updateNotificationsConfig(body)
        print(r[0])

    def testTestNotificationsEmail(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.testNotificationsEmail(body)
        print(r[0])

    def testResetNotificationsTimes(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        body = {}
        r = notifications.resetNotificationsTimes(body)
        print(r[0])


if __name__ == '__main__':
    unittest.main()  
