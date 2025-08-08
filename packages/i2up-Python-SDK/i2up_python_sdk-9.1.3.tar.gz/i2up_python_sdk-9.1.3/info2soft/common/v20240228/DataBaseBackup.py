
from info2soft import config
from info2soft import https


class DataBaseBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 导入导出-配置导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importConfig(self, body):
        
        url = '{0}/cc/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 导入导出-配置导出
     * 
     * @return list
    '''
    def exportConfig(self, body):
        
        url = '{0}/cc/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动备份-备份历史
     * 
     * @return list
    '''
    def listBackupHistory(self, body):
        
        url = '{0}/cc/backup_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动备份-备份配置
     * 
     * @return list
    '''
    def backupConfig(self, body):
        
        url = '{0}/cc/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 自动备份-备份配置详情
     * 
     * @return list
    '''
    def describeBackupConfig(self, body):
        
        url = '{0}/cc/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

