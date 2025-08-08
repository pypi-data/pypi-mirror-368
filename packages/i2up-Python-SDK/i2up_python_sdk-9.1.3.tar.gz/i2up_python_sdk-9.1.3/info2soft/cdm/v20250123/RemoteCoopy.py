
from info2soft import config
from info2soft import https


class RemoteCoopy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 环境检测 -- 目标机器是否存在重复规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyDuplicateCdmCoopyRule(self, body):
        
        url = '{0}/cdm_remote_coopy/verify_duplicate_cdm_coopy_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 列表获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 远程复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def migrateCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startImmediatelyCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRemoteCoopyStatus(self, body):
        
        url = '{0}/cdm_remote_coopy/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 远程复制 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCdmRemoteCoopy(self, body):
        
        url = '{0}/cdm_remote_coopy'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 远程复制规则单独获取
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdmRemoteCoopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_remote_coopy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 环境检测 -- 存储空间容量检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyCdmCapacity(self, body):
        
        url = '{0}/cdm_remote_coopy/verify_cdm_capacity'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * CDM 检查原备存储是否有多余CDM许可
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRemoteCoopyLicense(self, body):
        
        url = '{0}/cdm_remote_coopy/verify_license'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * CDM 目标存储已存在目录检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyCdmDirExist(self, body):
        
        url = '{0}/cdm_remote_coopy/verify_dir_exist'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

