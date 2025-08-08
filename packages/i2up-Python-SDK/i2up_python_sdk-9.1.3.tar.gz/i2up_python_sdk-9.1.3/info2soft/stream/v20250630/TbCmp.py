
from info2soft import config
from info2soft import https


class TbCmp (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncTbCmpStatus(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpStopTime(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpResumeTime(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpImmediate(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncTbCmpResult(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpErrorMsg(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportSyncTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

