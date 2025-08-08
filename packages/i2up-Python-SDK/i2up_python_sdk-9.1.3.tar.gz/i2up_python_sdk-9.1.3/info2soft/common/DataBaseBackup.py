
from info2soft import config
from info2soft import https


class DataBaseBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 配置导入
     * 
     * @return array
     '''
    def importConfig(self, body):
        
        url = '{0}/cc/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置导出
     * 
     * @return array
     '''
    def exportConfig(self, ):
        
        url = '{0}/cc/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份历史
     * 
     * @return array
     '''
    def listBackupHistory(self, ):
        
        url = '{0}/cc/backup_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份配置
     * 
     * @return array
     '''
    def backupConfig(self, ):
        
        url = '{0}/cc/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, None, self.auth)
        return res

    '''
     * 备份配置详情
     * 
     * @return array
     '''
    def describeBackupConfig(self, ):
        
        url = '{0}/cc/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

