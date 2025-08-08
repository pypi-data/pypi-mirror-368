
# -*- coding: utf-8 -*-
# flake8: noqa
import sys

import unittest
from info2soft.resource.v20200930.ServiceCluster import ServiceCluster
# from info2soft.resource.v20200722.ServiceCluster import ServiceCluster
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


class ServiceClusterTestCase(unittest.TestCase):

    def testCreateServiceCls(self):
        a = Auth(username, pwd)
        body = {
            'service_cls': {
            'cls_name': '',
            'label_list': [],
            'cls_node': [{
            'hostname': '',
            'ip': '',
            'port': '',
            'version': ''}],
            'service_type': [],
            'bind_lic_list': [],
            'cc_ip_uuid': '',
            'cc_ip': '',
            'os_type': 1,
            'etcd_url_uuid': '',
            'etcd_url': [{
            'ip': '',
            'port': ''}]},
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.createServiceCls(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'createServiceCls', body)

    def testModifyServiceCls(self):
        a = Auth(username, pwd)
        body = {
            'service_cls': {
            'cls_name': 'svc1',
            'cls_uuid': 'AB790C28-62D6-7236-612F-65D73C80036F',
            'label_list': [],
            'random_str': 'AB790B28-62D6-7236-612F-65D73C80036F',
            'cls_node': [{
            'hostname': '',
            'ip': '',
            'port': ''}],
            'service_type': [],
            'bind_lic_list': []},
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.modifyServiceCls(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'modifyServiceCls', body)

    def testDeleteServiceCls(self):
        a = Auth(username, pwd)
        body = {
            'cls_uuids': [],
            'force': 1,
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.deleteServiceCls(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'deleteServiceCls', body)

    def testDescribeServiceCls(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.describeServiceCls(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'describeServiceCls', body)

    def testListServiceCls(self):
        a = Auth(username, pwd)
        body = {
            'limit': 1,
            'search_value': '',
            'search_field': '',
            'page': 1,
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.listServiceCls(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'listServiceCls', body)

    def testListServiceClsStatus(self):
        a = Auth(username, pwd)
        body = {
            'cls_uuids': [],
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.listServiceClsStatus(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'listServiceClsStatus', body)

    def testChkServiceClsNode(self):
        a = Auth(username, pwd)
        body = {
            'cls_uuid': '',
            'node_uuid': '',
        }
        
        serviceCluster = ServiceCluster(a)
        r = serviceCluster.chkServiceClsNode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'ServiceCluster', 'chkServiceClsNode', body)


if __name__ == '__main__':
    unittest.main()
