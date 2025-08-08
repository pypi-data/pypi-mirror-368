
from info2soft import config
from info2soft import https


class MountTask (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMountTask(self, body):
        
        url = '{0}/mount_task'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @return list
    '''
    def listMountTask(self, body):
        
        url = '{0}/mount_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeMountTask(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mount_task/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMountTask(self, body):
        
        url = '{0}/mount_task'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMountTaskStatus(self, body):
        
        url = '{0}/mount_task/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取客户端iscsi
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getIscsiInitiatorInfo(self, body):
        
        url = '{0}/mount_task/iscsi_initiator_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取快照CLONE TARGET
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVolumeSnapshotTarget(self, body):
        
        url = '{0}/mount_task/volume_snapshot_target'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除快照CLONE_TARGET
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolumeSnapshotTarget(self, body):
        
        url = '{0}/mount_task/volume_snapshot_target'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

