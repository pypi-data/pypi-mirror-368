
from info2soft import config
from info2soft import https


class Dashboard (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 资源概览（旧）
     * 
     * @return list
    '''
    def resourceView(self, body):
        
        url = '{0}/dashboard/source'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 资源概览 - 获取资源池列表
     * 
     * @return list
    '''
    def listBackupCenter(self, body):
        
        url = '{0}/dashboard/list_backup_center'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 资源概览 - 获取资源使用率和保护覆盖率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getBackupCenterInfo(self, body):
        
        url = '{0}/dashboard/backup_center_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源概览 - 获取接管、演练平台列表
     * 
     * @return list
    '''
    def listHosts(self, body):
        
        url = '{0}/dashboard/list_hosts'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 设置资源保护覆盖率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resourceProtectionCoverage(self, body):
        
        url = '{0}/dashboard/resource_protection_coverage'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 任务概览列表
     * 
     * @return list
    '''
    def taskView(self, body):
        
        url = '{0}/dashboard/task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 5 Dashboard - 获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def repBackup(self, body):
        
        url = '{0}/dashboard/rep'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Dashboard - 高可用列表
     * 
     * @return list
    '''
    def ha(self, body):
        
        url = '{0}/dashboard/ha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 Dashboard - 获取节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def node(self, body):
        
        url = '{0}/dashboard/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

