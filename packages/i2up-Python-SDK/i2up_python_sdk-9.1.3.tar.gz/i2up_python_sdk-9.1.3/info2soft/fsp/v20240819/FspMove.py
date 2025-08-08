
from info2soft import config
from info2soft import https


class FspMove (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 1 检测迁移条件-获取两节点网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspMoveNic(self, body):
        
        url = '{0}/fsp/move/nic_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件-获取源节点磁盘和文件列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspMoveDir(self, body):
        
        url = '{0}/fsp/move/dir_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件-检测迁移条件-磁盘
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspMoveVolumeSpace(self, body):
        
        url = '{0}/fsp/move/verify_volume_space'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件-检测迁移条件-license
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspMoveLicense(self, body):
        
        url = '{0}/fsp/move/verify_license'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件-检测迁移条件-旧规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspMoveOldRule(self, body):
        
        url = '{0}/fsp/move/verify_old_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件-检测迁移条件-系统版本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspMoveOsVersion(self, body):
        
        url = '{0}/fsp/move/verify_os_version'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测迁移条件 - 环境监测
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspMoveEnvironment(self, body):
        
        url = '{0}/fsp/move/verify_environment'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 检测迁移条件 - 获取节点网络配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeNetworks(self, body):
        
        url = '{0}/fsp/move/networks'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建 - 准备 - 获取源端驱动列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspMoveDriverInfo(self, body):
        
        url = '{0}/fsp/move/driver_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2 新建/编辑-新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFspMove(self, body):
        
        url = '{0}/fsp/move'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 新建/编辑-获取单个规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFspMove(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/move/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 2 新建/编辑-修改规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFspMove(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/move/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 3 列表-删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFspMove(self, body):
        
        url = '{0}/fsp/move'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 3 列表-获取规则列表（基本信息）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspMove(self, body):
        
        url = '{0}/fsp/move'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3 列表-规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFspMove(self, body):
        
        url = '{0}/fsp/move/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 3 列表-规则状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspMoveStatus(self, body):
        
        url = '{0}/fsp/move/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 业务迁移 - 批量创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateFspMove(self, body):
        
        url = '{0}/fsp/move/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

