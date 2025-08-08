
from info2soft import config
from info2soft import https


class Lic (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 1 获取激活所需信息（组激活，离线激活）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def describeActivateInfo(self, body):
        
        url = '{0}/lic/activate'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2 下载lic绑定信息、mac变更记录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def downloadLicInfo(self, body):
        if body is None or 'lic_uuid' not in body:
            exit()
        url = '{0}/lic/{1}/download_lic_info'.format(config.get_default('default_api_host'), body['lic_uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 获取控制机识别码
     * 
     * @return array
     '''
    def describeLicCcHwCode(self, ):
        
        url = '{0}/lic/cc_hw_code'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 4 获取节点识别码
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def describeLicObjHwCode(self, body):
        
        url = '{0}/lic/obj_hw_code'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 5 在线激活（激活所有许可并更新，页面下端）
     * 
     * @return array
     '''
    def activateLicAll(self, ):
        
        url = '{0}/lic/activate'.format(config.get_default('default_api_host'))
        
        res = https._put(url, None, self.auth)
        return res

    '''
     * 1 添加 lic
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def createLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 更新 lic
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def updateLic(self, body):
        
        url = '{0}/lic/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        del body['uuid']
        res = https._put(url, body, self.auth)
        return res

    '''
     * 2 更新 lic（批量，离线）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def updateBatchLic(self, body):
        
        url = '{0}/lic/batch'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 5 获取单个 lic
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def describeLic(self, body):
        if body is None or 'lic_uuid' not in body:
            exit()
        url = '{0}/lic/{1}'.format(config.get_default('default_api_host'), body['lic_uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 6 获取 lic 列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 7 删除 lic
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def deleteLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 2 获取 Lic 绑定情况 列表（节点/VP管理）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listLicObjBind(self, body):
        
        url = '{0}/lic/obj_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2 获取 Lic 绑定情况 列表（许可管理）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listLicBind(self, body):
        
        url = '{0}/lic/lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 更新绑定（许可管理）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def updateLicBind(self, body):
        
        url = '{0}/lic/lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 1 获取 Obj 列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listLicObj(self, body):
        
        url = '{0}/lic/obj'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

