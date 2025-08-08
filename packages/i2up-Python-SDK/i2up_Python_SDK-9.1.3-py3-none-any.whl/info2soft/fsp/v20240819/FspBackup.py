
from info2soft import config
from info2soft import https


class FspBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 全服备份-0 获取两节点网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupNic(self, body):
        
        url = '{0}/fsp/backup/nic_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服备份-0 获取源节点磁盘和文件列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupDir(self, body):
        
        url = '{0}/fsp/backup/dir_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服备份-1 检测条件-备份空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspBackupCoopySpace(self, body):
        
        url = '{0}/fsp/backup/verify_coopy_space'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-1 检测条件-license
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspBackupLicense(self, body):
        
        url = '{0}/fsp/backup/verify_license'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-1 检测条件-旧规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspBackupOldRule(self, body):
        
        url = '{0}/fsp/backup/verify_old_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-1 检测条件-系统版本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyFspBackupOsVersion(self, body):
        
        url = '{0}/fsp/backup/verify_os_version'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服务器备份 - 获取节点设备列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupDriverInfo(self, body):
        
        url = '{0}/fsp/backup/device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服备份-2 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-2 修改规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFspBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 全服备份-2 获取单个规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFspBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/fsp/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 全服备份-3 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 全服备份-3 获取规则列表（基本信息）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def finishFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failoverFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failbackFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 全服备份-3 规则状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFspBackupStatus(self, body):
        
        url = '{0}/fsp/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机备份 - 批量创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateFspBackup(self, body):
        
        url = '{0}/fsp/backup/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 环境检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyEnvironment(self, body):
        
        url = '{0}/fsp/backup/verify_environment'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

