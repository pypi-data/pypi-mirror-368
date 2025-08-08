
from info2soft import config
from info2soft import https


class FspRecovery (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 全服恢复-0 获取两节点网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryNic(self, body):
        
        url = '{0}/fsp/recovery/nic_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复-0 获取源节点磁盘和文件列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryDir(self, body):
        
        url = '{0}/fsp/recovery/dir_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复-0 获取还原点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryPoint(self, body):
        
        url = '{0}/fsp/recovery/point_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复-1 检测条件-磁盘空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspRecoveryVolumeSpace(self, body):
        
        url = '{0}/fsp/recovery/verify_volume_space'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-1 检测条件-旧规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspRecoveryOldRule(self, body):
        
        url = '{0}/fsp/recovery/verify_old_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-1 检测条件-系统版本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspRecoveryOsVersion(self, body):
        
        url = '{0}/fsp/recovery/verify_os_version'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-2 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFspRecovery(self, body):
        
        url = '{0}/fsp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-2 修改规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFspRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 全服恢复-2 获取单个规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def desribeFspRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 全服恢复-3 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFspRecovery(self, body):
        
        url = '{0}/fsp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 获取规则列表（基本信息）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecovery(self, body):
        
        url = '{0}/fsp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFspRecovery(self, body):
        
        url = '{0}/fsp/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopFspRecovery(self, body):
        
        url = '{0}/fsp/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def moveFspRecovery(self, body):
        
        url = '{0}/fsp/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebootFspRecovery(self, body):
        
        url = '{0}/fsp/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服恢复-3 规则状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryStatus(self, body):
        
        url = '{0}/fsp/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复-获取磁盘信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspRecoveryDriverInfo(self, body):
        
        url = '{0}/fsp/recovery/driver_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服恢复 - 目标机驱动URL列表
     * 
     * @return list
    '''
    def listFspRecoveryDriverListUrl(self, body):
        
        url = '{0}/fsp/recovery/driver_url_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 全服恢复 - 0 获取BIOS类型
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getFspMoveBiosType(self, body):
        
        url = '{0}/fsp/move/bios_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

