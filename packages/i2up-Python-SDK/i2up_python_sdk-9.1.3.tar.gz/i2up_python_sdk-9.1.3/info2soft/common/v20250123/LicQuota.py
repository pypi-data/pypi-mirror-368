
from info2soft import config
from info2soft import https


class LicQuota (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 许可配额 - 总览
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def quotaOverview(self, body):
        
        url = '{0}/lic_quota/quota_overview'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 许可配额 - 新增
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createLicQuota(self, body):
        
        url = '{0}/lic_quota'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 许可配额 - 退订
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def unsubscribeLicQuota(self, body):
        
        url = '{0}/lic_quota'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 许可配额 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLicQuota(self, body):
        
        url = '{0}/lic_quota'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 许可配额 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeLicQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lic_quota/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 许可配额 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateLicQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lic_quota/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 许可配额 - 获取绑定情况
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getLicQuotaBindList(self, body):
        
        url = '{0}/lic_quota/lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

