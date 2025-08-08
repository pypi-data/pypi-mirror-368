
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

    def testListNotifications(self):
        a = Auth(username, pwd)
        body = {
            'type': 1,
            'where_args[status]': 1,
        }
        notifications = Notifications(a)
        r = notifications.listNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'listNotifications', body)

    def testDescribeNotifications(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '56BC2F93-9E39-9418-D2FD-0F3103B42429'
        }
        notifications = Notifications(a)
        r = notifications.describeNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotifications', body)

    def testDescribeNotificationsCount(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        r = notifications.describeNotificationsCount()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotificationsCount', {})

    def testDeleteNotifications(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'delete',
            'uuids': ['56BC2F93-9E39-9418-D2FD-0F3103B42429'],
            'type': 1,
        }
        notifications = Notifications(a)
        r = notifications.deleteNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'deleteNotifications', body)

    def testReadNotifications(self):
        a = Auth(username, pwd)
        body = {
            'operate': 'read',
            'uuids': ['56BC2F93-9E39-9418-D2FD-0F3103B42429'],
            'type': 1,
        }
        notifications = Notifications(a)
        r = notifications.readNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'readNotifications', body)

    def testDescribeNotificationsConfig(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        r = notifications.describeNotificationsConfig()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotificationsConfig', {})

    def testUpdateNotificationsConfig(self):
        a = Auth(username, pwd)
        body = {
            'config': [
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {

                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                             },
                {
                    'type': 1,
                    'email_sw': 0,
                    'sms_sw': 1,
                    'p_sms_sw': 1,
                }
            ],
        }
        notifications = Notifications(a)
        r = notifications.updateNotificationsConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'updateNotificationsConfig', body)

    def testTestNotificationsEmail(self):
        a = Auth(username, pwd)
        body = {
            'email': 'lis@info2soft.com',
        }
        notifications = Notifications(a)
        r = notifications.testNotificationsEmail(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'testNotificationsEmail', body)

    def testResetNotificationsTimes(self):
        a = Auth(username, pwd)
        notifications = Notifications(a)
        r = notifications.resetNotificationsTimes()
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'resetNotificationsTimes', {})


if __name__ == '__main__':
    unittest.main()  
