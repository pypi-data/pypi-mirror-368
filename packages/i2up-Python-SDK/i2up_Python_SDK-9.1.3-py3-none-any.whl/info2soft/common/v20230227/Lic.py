
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
     * 其他 - 下载lic绑定信息、mac变更记录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def downloadLicInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lic/{1}/download_lic_info'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 其他 - 获取控制机识别码
     * 
     * @return list
    '''
    def describeLicCcHwCode(self, body):
        
        url = '{0}/lic/cc_hw_code'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 其他 - 获取节点识别码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeLicObjHwCode(self, body):
        
        url = '{0}/lic/obj_hw_code'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 其他 - 在线更新
     * 
     * @return list
    '''
    def activateLicAll(self, body):
        
        url = '{0}/lic/activate'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Lic - 获取 lic 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Lic - 添加 lic
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Lic-7 删除 lic
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteLic(self, body):
        
        url = '{0}/lic'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * Lic - 更新 lic（批量，离线）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateBatchLic(self, body):
        
        url = '{0}/lic/batch'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Lic - 获取单个 lic
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeLic(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lic/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 绑定 - 获取许可绑的资源（许可管理）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLicBind(self, body):
        
        url = '{0}/lic/lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 绑定 - 获取资源绑的许可（节点/VP管理）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLicObjBind(self, body):
        
        url = '{0}/lic/obj_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 绑定 - 更新许可绑的资源（许可管理）
     * 
     * @return list
    '''
    def updateLicBind(self, body):
        
        url = '{0}/lic/lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Obj - 获取 Obj 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLicObj(self, body):
        
        url = '{0}/lic/obj'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CDM容量管理
     * 
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
     * 其他 - Move已占用节点及其识别码
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeMoveLicBind(self, body):
        
        url = '{0}/lic/move_lic_bind'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * hdfs容量管理
     * 
     * @return list
    '''
    def hdfsCapacity(self, body):
        
        url = '{0}/lic/hdfs_capacity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

