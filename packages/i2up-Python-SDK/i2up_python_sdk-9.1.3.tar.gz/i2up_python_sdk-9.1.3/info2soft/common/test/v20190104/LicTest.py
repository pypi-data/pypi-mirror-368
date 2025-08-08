
# -*- coding: utf-8 -*-
# flake8: noqa
import sys
sys.path.append(r'E:/python-sdk')

import unittest
from info2soft.common.Lic import Lic
# from info2soft.common.v20200722.Lic import Lic
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


class LicTestCase(unittest.TestCase):

    def testDescribeActivateInfo(self):
        a = Auth(username, pwd)
        body = {
            'group_sn': '20-4570098558',
        }
        
        lic = Lic(a)
        r = lic.describeActivateInfo(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'describeActivateInfo', body)

    def testDownloadLicInfo(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        lic = Lic(a)
        r = lic.downloadLicInfo(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'downloadLicInfo', body)

    def testDescribeLicCcHwCode(self):
        a = Auth(username, pwd)
        body = {
        }
        
        lic = Lic(a)
        r = lic.describeLicCcHwCode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'describeLicCcHwCode', body)

    def testDescribeLicObjHwCode(self):
        a = Auth(username, pwd)
        body = {
            'obj_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        lic = Lic(a)
        r = lic.describeLicObjHwCode(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'describeLicObjHwCode', body)

    def testActivateLicAll(self):
        a = Auth(username, pwd)
        body = {
        }
        
        lic = Lic(a)
        r = lic.activateLicAll(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'activateLicAll', body)

    def testListLic(self):
        a = Auth(username, pwd)
        body = {
            'search_value': '',
            'search_field': '',
            'direction': '',
            'page': 1,
            'limit': 1,
            'order_by': '',
        }
        
        lic = Lic(a)
        r = lic.listLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'listLic', body)

    def testCreateLic(self):
        a = Auth(username, pwd)
        body = {
            'num': 1,
            'sn': [
            '20-4570098558-01',],
            'key': '5BrDir',
            'sign': '',
            'license': {
            '20-4570098558-01': {
            'feature': 'cdp',
            'lic': 'joEsLGQImYbDo2/DSG2RGR7VorckQmnPAAvFgLNCVd78KFDFb0Y0xtShHFyQVF6VXRUcHvyeqJEu1/nuMOyyJiO8RMoU4GHZMrK6iLDRoPZHV87tp0Jd80MfuTHrpBc209IjM+AkSsTM66Wdfy0tvLJMfPqhaYdg7M80X+fhRfeP6kj9ikSVvmJMHJ/ms7lrgz5D+s9jhtzW7tv9cz07bbankTgwyZf6rnjbgOI76tsKzYq8rsBttYSGf+oy1qa2nM7x/pQHE6oRiXVy8+Ju2dzpwvLlMurF75r7lWyMRPSniPHBQGrx4yEEeKVwuWCMRaSJVyId13qyP7gPBqes4jgsiVHvt1okhydrAeoq89KOgnOHPqrpS+qI9dvXFmFRiP9AB0i9ra67tDx5ItYNh/neNgxsNpV3q0Tf9PfoTKiKwcYMg0AiFeKuSpynDIL530Ek8Jm/7LbXU7+mUkeGO7BJo9gxEMJRTHuSRLCLIXWm2LY2S58WccsXkL7GFaamkh6lE1VX3quXavLpHC0ishL4D0ocEdAh507s6GKd59oVErFAyBOifEE9EONR+95wD9MQMc4SdNt4l4Z7ATj67JN86UFZ5xZpGEOnMgCSUuuzX/Nx0HSF6uUf3Zs6HcViudmXcvLwwaFeRScRDwHYVLhiABda/qAp8Ovoc8Aw/3w=',},},
        }
        
        lic = Lic(a)
        r = lic.createLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'createLic', body)

    def testUpdateBatchLic(self):
        a = Auth(username, pwd)
        body = {
            'num': 1,
            'sn': [
            '20-4570098558-01',],
            'key': '5BrDir',
            'sign': '',
            'license': {
            '20-4570098558-01': {
            'feature': 'cdp',
            'lic': 'joEsLGQImYbDo2/DSG2RGR7VorckQmnPAAvFgLNCVd78KFDFb0Y0xtShHFyQVF6VXRUcHvyeqJEu1/nuMOyyJiO8RMoU4GHZMrK6iLDRoPZHV87tp0Jd80MfuTHrpBc209IjM+AkSsTM66Wdfy0tvLJMfPqhaYdg7M80X+fhRfeP6kj9ikSVvmJMHJ/ms7lrgz5D+s9jhtzW7tv9cz07bbankTgwyZf6rnjbgOI76tsKzYq8rsBttYSGf+oy1qa2nM7x/pQHE6oRiXVy8+Ju2dzpwvLlMurF75r7lWyMRPSniPHBQGrx4yEEeKVwuWCMRaSJVyId13qyP7gPBqes4jgsiVHvt1okhydrAeoq89KOgnOHPqrpS+qI9dvXFmFRiP9AB0i9ra67tDx5ItYNh/neNgxsNpV3q0Tf9PfoTKiKwcYMg0AiFeKuSpynDIL530Ek8Jm/7LbXU7+mUkeGO7BJo9gxEMJRTHuSRLCLIXWm2LY2S58WccsXkL7GFaamkh6lE1VX3quXavLpHC0ishL4D0ocEdAh507s6GKd59oVErFAyBOifEE9EONR+95wD9MQMc4SdNt4l4Z7ATj67JN86UFZ5xZpGEOnMgCSUuuzX/Nx0HSF6uUf3Zs6HcViudmXcvLwwaFeRScRDwHYVLhiABda/qAp8Ovoc8Aw/3w=',},},
            'is_trial': 1,
        }
        
        lic = Lic(a)
        r = lic.updateBatchLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'updateBatchLic', body)

    def testDescribeLic(self):
        a = Auth(username, pwd)
        body = {
        }
        uuid = "22D03E06-94D0-5E2C-336E-4BEEC2D28EC4"
        lic = Lic(a)
        r = lic.describeLic(body, uuid)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'describeLic', body)

    def testDeleteLic(self):
        a = Auth(username, pwd)
        body = {
            'lic_uuids': [
            '11111111-1111-1111-1111-111111111111',],
        }
        
        lic = Lic(a)
        r = lic.deleteLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'deleteLic', body)

    def testListLicBind(self):
        a = Auth(username, pwd)
        body = {
            'lic_uuid': '11111111-1111-1111-1111-111111111111',
        }
        
        lic = Lic(a)
        r = lic.listLicBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'listLicBind', body)

    def testListLicObjBind(self):
        a = Auth(username, pwd)
        body = {
            'obj_uuid': '11111111-1111-1111-1111-111111111111',
            'obj_type': 0,
            'config_addr': '192.168.72.76',
            'config_port': '26821',
            'proxy_switch': 1,
            'i2id': '',
            'obj_subtype': 1,
        }
        
        lic = Lic(a)
        r = lic.listLicObjBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'listLicObjBind', body)

    def testUpdateLicBind(self):
        a = Auth(username, pwd)
        body = {
            'obj_uuids': [
            '11111111-1111-1111-1111-111111111111',],
            'lic_uuid': '11111111-1111-1111-1111-111111111111',
        }
        
        lic = Lic(a)
        r = lic.updateLicBind(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'updateLicBind', body)

    def testListLicObj(self):
        a = Auth(username, pwd)
        body = {
            'feature': 'coopy',
            'obj_type': 0,
            'where_args[obj_uuid]': '11111111-1111-1111-1111-111111111111',
            'filter_by_biz_grp': '1',
            'obj_subtype': 1,
            'where_args[os_type]': '',
            'order_by': '',
            'direction': '',
        }
        
        lic = Lic(a)
        r = lic.listLicObj(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'listLicObj', body)

    def testCdmCapacity(self):
        a = Auth(username, pwd)
        body = {
        }
        
        lic = Lic(a)
        r = lic.cdmCapacity(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'cdmCapacity', body)

    def testUnsubscribeLic(self):
        a = Auth(username, pwd)
        body = {
            'sn': '',
            'operate': 'unsubscribe',
        }

        lic = Lic(a)
        r = lic.unsubscribeLic(body)
        print(r[0])
        assert r[0]['ret'] == 200
        write(r[0], 'Lic', 'unsubscribeLic', body)


if __name__ == '__main__':
    unittest.main()
