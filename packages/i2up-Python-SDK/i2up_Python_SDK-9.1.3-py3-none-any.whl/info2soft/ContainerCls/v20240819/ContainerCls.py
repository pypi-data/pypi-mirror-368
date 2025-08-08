
from info2soft import config
from info2soft import https


class ContainerCls (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createContinerClusterBackup(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterBackup(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeContainerClusterBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/v3/container_cluster_protect/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyContainerClusterBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/v3/container_cluster_protect/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteContainerClusterBackup(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterBackupStatus(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def backupImmediateContainerClusterBackup(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 查看子任务列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterBackupSubTask(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup/sub_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 查看备份信息(rpc获取)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getContainerClusterBackupInfo(self, body):
        
        url = '{0}/v3/container_cluster_protect/backup/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createContainerClusterRecovery(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 还原 - 列表
     * 
     * @return list
    '''
    def listContainerClusterRecovery(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 还原 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeContainerClusterRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/v3/container_cluster_protect/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 还原 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyContainerClusterRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/v3/container_cluster_protect/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 还原 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteContainerClusterRecovery(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 还原 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterRecoveryStatus(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 获取还原时间点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterRecoveryPoint(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery/rc_point'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startContainerClusterRecovery(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 还原 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopContainerClusterRecovery(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 还原 - 查看还原信息(rpc获取)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getContainerClusterRecoveryInfo(self, body):
        
        url = '{0}/v3/container_cluster_protect/recovery/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

