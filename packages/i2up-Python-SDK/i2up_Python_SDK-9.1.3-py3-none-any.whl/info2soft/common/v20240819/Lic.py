
from info2soft import config
from info2soft import https


class Lic (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 其他 - 获取激活所需信息（组激活，离线激活）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeActivateInfo(self, body):
        
        url = '{0}/lic/activate'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CDM容量管理
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cdmCapacity(self, body):
        
        url = '{0}/lic/cdm_capacity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Lic - 退订操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def unsubscribeLic(self, body):
        
        url = '{0}/lic/unsubscribe'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs容量管理
     * 
     * @return list
    '''
    def hdfsCapacity(self, body):
        
        url = '{0}/lic/hdfs_capacity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Lic - 即将过期提示许可列表
     * 
     * @return list
    '''
    def listNearExpirationLicenses(self, body):
        
        url = '{0}/lic/list_near_expiration'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Lic - 更新许可 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateLic(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lic/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * VP许可授权详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVpAuthDetail(self, body):
        
        url = '{0}/lic/vp_auth_detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * LIC - 获取节点列表（sysadmin角色下无用户权限过滤）
     * 
     * @return list
    '''
    def getNodeListForLicense(self, body):
        
        url = '{0}/lic/node_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Backup9授权详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLicBackupAuthDetail(self, body):
        
        url = '{0}/lic/backup9_auth_detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 消息 - 许可消息弹窗
     * 
     * @return list
    '''
    def listLicAlert(self, body):
        
        url = '{0}/lic/list_alert'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 许可弹窗消息 - 不再提醒
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def avoidAlert(self, body):
        
        url = '{0}/lic/forbid_alert'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

