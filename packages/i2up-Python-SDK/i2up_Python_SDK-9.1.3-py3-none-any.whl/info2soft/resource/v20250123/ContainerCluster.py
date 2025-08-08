
from info2soft import config
from info2soft import https


class ContainerCluster (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份目标位置 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackupDestination(self, body):
        
        url = '{0}/backup_destination'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份目标位置 - 列表
     * 
     * @return list
    '''
    def listBackupDestination(self, body):
        
        url = '{0}/backup_destination'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份目标位置 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descibeBackupDestination(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_destination/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份目标位置 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBackupDestination(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_destination/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份目标位置 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupDestination(self, body):
        
        url = '{0}/backup_destination'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份目标位置 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupDestinationStatus(self, body):
        
        url = '{0}/backup_destination/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 容器集群 - 集群信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterInfo(self, body):
        
        url = '{0}/container_cluster/cls_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 容器集群 - 同步信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncContainerClusterInfo(self, body):
        
        url = '{0}/container_cluster/sync_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 容器集群 - 资源信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClusterResource(self, body):
        
        url = '{0}/container_cluster/resource'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 容器集群 - 名字空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listContainerClsNamespace(self, body):
        
        url = '{0}/container_cluster/namespace'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 容器集群-概览-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def containerClusterMonitoringOverview(self, body):
        
        url = '{0}/v3/container_cluster/monitoring/overview'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 容器集群-概览-节点
     * 
     * @return list
    '''
    def containerClusterMonitoringNode(self, body):
        
        url = '{0}/v3/container_cluster/monitoring/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 容器集群 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createContainerCluster(self, body):
        
        url = '{0}/container_cluster'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 容器集群 - 列表
     * 
     * @return list
    '''
    def listContainerCluster(self, body):
        
        url = '{0}/container_cluster'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 容器集群 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeContainerCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/container_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 容器集群 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyContainerCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/container_cluster/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 容器集群 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteContainerCluster(self, body):
        
        url = '{0}/container_cluster'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 回调设置 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCallbackSettings(self, body):
        
        url = '{0}/callback_settings'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 回调设置 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCallbackSettings(self, body):
        
        url = '{0}/callback_settings'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 回调设置 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCallbackSettings(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/callback_settings/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 回调设置 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCallbackSettings(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/callback_settings/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 回调设置 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCallbackSettings(self, body):
        
        url = '{0}/callback_settings'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 回调设置 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cloneCallbackSettings(self, body):
        
        url = '{0}/callback_settings/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 回调设置 - 验证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyCallbackSettingsPod(self, body):
        
        url = '{0}/callback_settings/pod_verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

