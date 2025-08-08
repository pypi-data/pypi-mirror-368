
from info2soft import config
from info2soft import https


class RemoteRep (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 远程复制 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRemoteRep(self, body):
        
        url = '{0}/remote_rep'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRemoteRep(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/remote_rep/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 远程复制 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRemoteRep(self, body):
        
        url = '{0}/remote_rep'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 远程复制 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRemoteRep(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/remote_rep/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 远程复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateRemoteRep(self, body):
        
        url = '{0}/remote_rep/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 远程复制 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRemoteRep(self, body):
        
        url = '{0}/remote_rep'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 远程复制 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRemoteRepStatus(self, body):
        
        url = '{0}/remote_rep/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 根据存储池获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStoragePoolRuleList(self, body):
        
        url = '{0}/remote_rep/storage_pool_rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 根据存储池获取文件系统列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFileSystem(self, body):
        
        url = '{0}/remote_rep/file_system'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取（二级）副本卷
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeCloneVolume(self, body):
        
        url = '{0}/remote_rep/clone_volume'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 根据备份规则过滤存储节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def filterStorageNode(self, body):
        
        url = '{0}/remote_rep/filter_storage'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 远程恢复 - 文件合成备份还原时间点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFileSnapshot(self, body):
        
        url = '{0}/remote_rep/file_snapshot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

