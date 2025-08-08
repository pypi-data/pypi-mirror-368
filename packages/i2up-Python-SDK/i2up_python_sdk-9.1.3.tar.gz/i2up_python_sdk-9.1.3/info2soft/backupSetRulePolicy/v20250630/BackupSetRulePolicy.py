
from info2soft import config
from info2soft import https


class BackupSetRulePolicy (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份集复制策略 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createReplicaTask(self, body):
        
        url = '{0}/replica_task'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份集复制策略 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyReplicaTask(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica_task/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份集复制策略 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReplicaTask(self, body):
        
        url = '{0}/replica_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份集复制策略 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeReplicaTask(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica_task/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份集复制策略 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteReplicaTask(self, body):
        
        url = '{0}/replica_task'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

