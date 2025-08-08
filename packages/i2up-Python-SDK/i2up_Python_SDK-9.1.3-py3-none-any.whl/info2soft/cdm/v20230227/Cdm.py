
from info2soft import config
from info2soft import https


class Cdm (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 自动演练规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdmDrill(self, body):
        
        url = '{0}/cdm_drill'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdmDrill(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_drill/group/([a-f0-9-] ){1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 自动演练规则 - 获取组
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdmDrillGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_drill/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 自动演练规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCdmDrill(self, body):
        
        url = '{0}/cdm_drill'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmDrillStatus(self, body):
        
        url = '{0}/cdm_drill/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCdmDrill(self, body):
        
        url = '{0}/cdm_drill/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动演练规则 - 获取虚机状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def queryGroupVmStatus(self, body):
        
        url = '{0}/cdm_drill/vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机复制 --- 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdm(self, body):
        
        url = '{0}/cdm'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机复制 --- 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCdm(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机复制 --- 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCdm(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 整机复制 --- 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdm(self, body):
        
        url = '{0}/cdm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机复制 --- 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmStatus(self, body):
        
        url = '{0}/cdm/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机复制 --- 根据工作机获取规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getByWk(self, body):
        
        url = '{0}/cdm/get_by_wk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getPointList(self, body):
        
        url = '{0}/cdm/point_full_info_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getNetworkList(self, body):
        
        url = '{0}/cdm/network_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFfomount(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ffo_mount/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 根据存储获取工作机列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getNodeList(self, body):
        
        url = '{0}/cdm/restore_node_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取资源列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getResourceList(self, body):
        
        url = '{0}/cdm/drp_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取主机存储资源
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getHostStorageList(self, body):
        
        url = '{0}/cdm/host_storage_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 按虚机恢复获取磁盘
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmInfo(self, body):
        
        url = '{0}/cdm/vm_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机恢复 --- 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmRecovery(self, body):
        
        url = '{0}/cdm_recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def takeOverDrillList(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTakeOverDrill(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cdm_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 接管/演练 --- 获取虚机状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmStatus(self, body):
        
        url = '{0}/cdm_rule/vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateTakeOverDrill(self, body):
        
        url = '{0}/cdm_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFfoMount(self, body):
        
        url = '{0}/ffo_mount'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFfoMount(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ffo_mount/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ffoMountList(self, body):
        
        url = '{0}/ffo_mount'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFfoMountStatus(self, body):
        
        url = '{0}/ffo_mount/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFfoMount(self, body):
        
        url = '{0}/ffo_mount'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 环境检测 -- Oracle是否开启归档
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyOracleArchiveMode(self, body):
        
        url = '{0}/cdm/verify_oracle_archive_mode'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 接管/演练 --- 自动演练
     * 
     * @return list
    '''
    def autoDrillCdmRule(self, body):
        
        url = '{0}/cdm_rule/'.format(config.get_default('default_api_host'))
        
        res = https._post(url, None, self.auth)
        return res

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
     * CDM 备份空间检查(弃用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyCdmRemoteCoopyDiskSpace(self, body):
        
        url = '{0}/cdm_remote_coopy/verify_disk_space'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

