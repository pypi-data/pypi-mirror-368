
from info2soft import config
from info2soft import https


class FspBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 0 获取两节点网卡列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listFspBackupNic(self, body):
        
        url = '{0}/fsp/backup/nic_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 0 获取源节点磁盘和文件列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listFspBackupDir(self, body):
        
        url = '{0}/fsp/backup/dir_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 检测条件-备份空间
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def verifyFspBackupCoopySpace(self, body):
        
        url = '{0}/fsp/backup/verify_coopy_space'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测条件-license
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def verifyFspBackupLicense(self, body):
        
        url = '{0}/fsp/backup/verify_license'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测条件-旧规则
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def verifyFspBackupOldRule(self, body):
        
        url = '{0}/fsp/backup/verify_old_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 检测条件-系统版本
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def verifyFspBackupOsVersion(self, body):
        
        url = '{0}/fsp/backup/verify_os_version'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 新建规则
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def createFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 修改规则
     * 
     * @body['fsp_backup']['fsp_uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def modifyFspBackup(self, body):
        
        url = '{0}/fsp/backup/{1}'.format(config.get_default('default_api_host'), body['fsp_backup']['fsp_uuid'])

        res = https._put(url, body, self.auth)
        return res

    '''
     * 2 获取单个规则
     * 
     * @body['fsp_backup']['fsp_uuid'] String  必填 节点uuid
     * @return array
     '''
    def describeFspBackup(self, body):
        if body is None or 'fsp_uuid' not in body['fsp_backup']:
            exit()
        url = '{0}/fsp/backup/{1}'.format(config.get_default('default_api_host'), body['fsp_backup']['fsp_uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 删除规则
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def deleteFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 3 获取规则列表（基本信息）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listFspBackup(self, body):
        
        url = '{0}/fsp/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3 规则操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def startFspBackup(self, body):
        
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    def stopFspBackup(self, body):
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    def finishFspBackup(self, body):
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    def failoverFspBackup(self, body):
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    def failbackFspBackup(self, body):
        url = '{0}/fsp/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 3 规则状态
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listFspBackupStatus(self, body):
        
        url = '{0}/fsp/backup/status'.format(config.get_default('default_api_host'))
        res = https._get(url, body, self.auth)
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
     * 整机备份 - 批量创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateFspBackup(self, body):

        url = '{0}/fsp/backup/batch'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

