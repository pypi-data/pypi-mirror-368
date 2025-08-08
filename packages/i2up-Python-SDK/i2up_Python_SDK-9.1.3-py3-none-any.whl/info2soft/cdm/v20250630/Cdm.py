
from info2soft import config
from info2soft import https


class Cdm (object):
    def __init__(self, auth):
        self.auth = auth
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
     * 整机复制 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCdm(self, body):
        
        url = '{0}/cdm'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
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
     * 获取备份点列表(刷新虚机规则对应关系)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDrillRestorePoint(self, body):
        
        url = '{0}/cdm/auto_drill_restore_point_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
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
     * 整机复制 - 数据库保护自定义脚本检测
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cdmScriptPathCheck(self, body):
        
        url = '{0}/cdm/script_path_check'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机复制 - 获取节点设备列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCdmDriverInfo(self, body):
        
        url = '{0}/cdm/device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

