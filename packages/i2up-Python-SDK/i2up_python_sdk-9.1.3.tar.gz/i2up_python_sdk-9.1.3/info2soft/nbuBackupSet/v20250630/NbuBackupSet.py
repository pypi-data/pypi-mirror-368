
from info2soft import config
from info2soft import https


class NbuBackupSet (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * NBU转储结果 - 历史结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupWork(self, body):
        
        url = '{0}/vers/v3/nbu_backup_set/history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * NBU转储结果 - 获取列表查询候选信息副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQueryArgsNbuBackupSet(self, body):
        
        url = '{0}/vers/v3/nbu_backup_set/query_args'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

