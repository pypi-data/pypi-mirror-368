
from info2soft import config
from info2soft import https


class GeneralSettings (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * etcd有效性检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def chkEtcdUrl(self, body):
        
        url = '{0}/etcd/etcd_url_chk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ETCD - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUpdateEtcd(self, body):
        
        url = '{0}/etcd'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ETCD - 列表
     * 
     * @return list
    '''
    def listEtcd(self, body):
        
        url = '{0}/etcd'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * ETCD - 发现
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanEtcdConf(self, body):
        
        url = '{0}/etcd/scan'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务调度器 - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUpdateScheduleSvr(self, body):
        
        url = '{0}/schedule_svr'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 服务调度器 - 列表
     * 
     * @return list
    '''
    def listScheduleSvr(self, body):
        
        url = '{0}/schedule_svr'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

