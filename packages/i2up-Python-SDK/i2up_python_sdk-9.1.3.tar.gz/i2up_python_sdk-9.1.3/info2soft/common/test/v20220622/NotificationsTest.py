# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Notifications import Notifications
# from info2soft.common.v20200722.Notifications import Notifications
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

    def testListNotifications(self):
        a = Auth(username, pwd)
        body = {
            'type': 1,
            'where_args[status]': 1,
            'order_by': 'status',
            'direction': 'ASC',
        }

        notifications = Notifications(a)
        r = notifications.listNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'listNotifications', body)

    def testDescribeNotifications(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        notifications = Notifications(a)
        r = notifications.describeNotifications(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotifications', body)

    def testDescribeNotificationsCount(self):
        a = Auth(username, pwd)
        body = {
        }

        notifications = Notifications(a)
        r = notifications.describeNotificationsCount(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotificationsCount', body)

    def testOperateNotifications(self):
        a = Auth(username, pwd)
        body = {
            'operate': '',
            'uuids': [],
            'type': 1,
        }

        notifications = Notifications(a)
        r = notifications.operateNotifications(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'operateNotifications', body)

    def testDescribeNotificationsConfig(self):
        a = Auth(username, pwd)
        body = {
        }

        notifications = Notifications(a)
        r = notifications.describeNotificationsConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'describeNotificationsConfig', body)

    def testUpdateNotificationsConfig(self):
        a = Auth(username, pwd)
        body = {
            'config': [{
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, {
                'type': 1,
                'email_sw': 0,
                'sms_sw': 1,
                'p_sms_sw': 1,
                'sms_temp': '', }, ],
        }

        notifications = Notifications(a)
        r = notifications.updateNotificationsConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'updateNotificationsConfig', body)

    def testTestNotificationsSms(self):
        a = Auth(username, pwd)
        body = {
            'temp_id': '',
            'mobile': '13123456789',
        }

        notifications = Notifications(a)
        r = notifications.testNotificationsSms(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'testNotificationsSms', body)

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
        body = {
        }

        notifications = Notifications(a)
        r = notifications.resetNotificationsTimes(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'resetNotificationsTimes', body)

    def testListEmailTemplate(self):
        a = Auth(username, pwd)
        body = {
            'order_by': 'status',
            'direction': 'ASC',
            'type': '',
        }

        notifications = Notifications(a)
        r = notifications.listEmailTemplate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'listEmailTemplate', body)

    def testModifyEmailTemplate(self):
        a = Auth(username, pwd)
        body = {
            'content': '',
            'comment': '',
            'random_str': '',
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        notifications = Notifications(a)
        r = notifications.modifyEmailTemplate(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'modifyEmailTemplate', body)

    def testOperateNotificationsTemplate(self):
        a = Auth(username, pwd)
        body = {
            'uuid': '',
            'operate': '',
        }

        notifications = Notifications(a)
        r = notifications.operateNotificationsTemplate(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Notifications', 'operateNotificationsTemplate', body)


if __name__ == '__main__':
    unittest.main()
