# -*- coding: utf-8 -*-
# flake8: noqa
import sys

sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Statistics import Statistics
# from info2soft.common.v20200722.Statistics import Statistics
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


class StatisticsTestCase(unittest.TestCase):

    def testListStatistics(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'end': 1,
            'name': '',
            'limit': 10,
            'start': 1,
            'status': '',
            'type': '',
            'result': 1,
            'group_uuid': '',
            'uuid': '',
            'time_used_rate': 1,
            'sub_type': 1,
            'obj_name': '',
            'time_consuming': 1,
            'wk_uuid': '',
            'bk_uuid': '',
            'other_uuid': '',
        }

        statistics = Statistics(a)
        r = statistics.listStatistics(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'listStatistics', body)

    def testDescribeStatistics(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        statistics = Statistics(a)
        r = statistics.describeStatistics(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'describeStatistics', body)

    def testReadStatistics(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'end': 1,
            'name': '',
            'limit': 10,
            'start': 1,
            'status': '',
            'type': '',
            'result': 1,
            'group_uuid': '',
            'uuid': '',
            'statistics_start': 1,
            'statistics_end': 1,
            'time_used_rate': 1,
            'sub_type': '',
            'obj_name': '',
            'time_consuming': 1,
            'wk_uuid': '',
            'bk_uuid': '',
            'other_uuid': '',
        }

        statistics = Statistics(a)
        r = statistics.readStatistics(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'readStatistics', body)

    def testListStatisticsChart(self):
        a = Auth(username, pwd)
        body = {
            'start': 1,
            'sub_type': '0',
            'end': 2,
            'type': 'vp',
            'page': 1,
            'limit': 10,
        }

        statistics = Statistics(a)
        r = statistics.listStatisticsChart(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'listStatisticsChart', body)

    def testUpdateStatisticsConfig(self):
        a = Auth(username, pwd)
        body = {
            'daily_report': {
                'daily_sw': 1,
                'daily_st': '11:43',
                'all_sw': 1,
                'bak_bk_sw': 1,
                'bak_rc_sw': 1,
                'cmp_sw': 1,
                'ffo_sw': 1,
                'rule_sw': 1,
                'vp_sw': 1,
            },
            'weekly_report': {
                'weekly_sw': '',
                'weekly_st': '1,00:00',
                'all_sw': 1,
                'bak_bk_sw': 1,
                'bak_rc_sw': 1,
                'cmp_sw': 1,
                'ffo_sw': 1,
                'rule_sw': 1,
                'vp_sw': 1,
            },
            'monthly_report': {
                'monthly_sw': '',
                'monthly_st': '1,00:00',
                'all_sw': 1,
                'bak_bk_sw': 1,
                'bak_rc_sw': 1,
                'cmp_sw': 1,
                'ffo_sw': 1,
                'rule_sw': 1,
                'vp_sw': 1,
            },
            'email': 'xxx@info2soft.com',
        }

        statistics = Statistics(a)
        r = statistics.updateStatisticsConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'updateStatisticsConfig', body)

    def testListStatisticsConfig(self):
        a = Auth(username, pwd)
        body = {
        }

        statistics = Statistics(a)
        r = statistics.listStatisticsConfig(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'listStatisticsConfig', body)

    def testDownloadStatistics(self):
        a = Auth(username, pwd)
        body = {
            'page': 1,
            'end': 1,
            'name': '',
            'limit': 10,
            'start': 1,
            'status': '',
            'type': '',
            'result': 1,
            'group_uuid': '',
            'uuid': '',
            'statistics_start': 1,
            'statistics_end': 1,
            'time_used_rate': 1,
            'src_type': 1,
            'obj_name': '',
            'time_consuming': 1,
            'wk_uuid': '',
            'bk_uuid': '',
            'other_uuid': '',
        }

        statistics = Statistics(a)
        r = statistics.downloadStatistics(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Statistics', 'downloadStatistics', body)


if __name__ == '__main__':
    unittest.main()
