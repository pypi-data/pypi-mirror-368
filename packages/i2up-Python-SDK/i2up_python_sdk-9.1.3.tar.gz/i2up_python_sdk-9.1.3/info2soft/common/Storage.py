from info2soft import config
from info2soft import https


class Storage (object):
    def __init__(self, auth):
        self.auth = auth

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createStorageConfig(self, body):
        url = '{0}/storage'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def modifyStorageConfig(self, body):
        url = '{0}/storage/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        del body['uuid']
        res = https._put(url, body, self.auth)
        return res

    '''
     *  获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
     '''

    def describeStorageConfig(self, body):
        if body is None or 'uuid' not in body: exit()
        url = '{0}/storage/{1}'.format(config.get_default('default_api_host'), body['uuid'])

        res = https._get(url, None, self.auth)
        return res

    '''
     *  获取列表
     * 
     * @return list
     '''

    def listStorageConfig(self, ):
        url = '{0}/storage'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteStorageConfig(self, body):
        url = '{0}/storage'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  容量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listStorageInfo(self, body):
        url = '{0}/storage/info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取可用节点列表
     * 
     * @return list
     '''

    def listAvailableNode(self, ):
        url = '{0}/storage/node'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res

    '''
     * ---------------------
     * 
     * @return list
     '''

    '''
     *  获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listDevice(self, body):
        url = '{0}/storage/dev'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取可用列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listAvailableDevice(self, body):
        url = '{0}/storage/available_dev'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * ---------------------
     * 
     * @return list
     '''

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createPool(self, body):
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  扩展
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def expandPool(self, body):
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deletePool(self, body):
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listPool(self, body):
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listPoolInfo(self, body):
        url = '{0}/storage/pool/info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * ---------------------
     * 
     * @return list
     '''

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createFs(self, body):
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteFs(self, body):
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listFs(self, body):
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createFsSnapshot(self, body):
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteFsSnapshot(self, body):
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listFsSnapshot(self, body):
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createFsCloneSnapshot(self, body):
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteFsCloneSnapshot(self, body):
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listFsCloneSnapshot(self, body):
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * ---------------------
     * 
     * @return list
     '''

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createVolume(self, body):
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteVolume(self, body):
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listVolume(self, body):
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createVolumeSnapshot(self, body):
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteVolumeSnapshot(self, body):
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listVolumeSnapshot(self, body):
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createVolumeCloneSnapshot(self, body):
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteVolumeCloneSnapshot(self, body):
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listVolumeCloneSnapshot(self, body):
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * ---------------------
     * 
     * @return list
     '''

    '''
     *  创建
     * 
     * @return list
     '''

    def create(self, ):
        url = '{0}/storage/vmdk'.format(config.get_default('default_api_host'))

        res = https._post(url, None, self.auth)
        return res

    '''
     *  删除
     * 
     * @return list
     '''

    def delete(self, ):
        url = '{0}/storage/vmdk'.format(config.get_default('default_api_host'))

        res = https._delete(url, None, self.auth)
        return res

    '''
     * --------------------- 存储区域网络（SAN）管理
     * 
     * @return list
     '''

    '''
     *  创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createBackStore(self, body):
        url = '{0}/storage/backstore'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteBackStore(self, body):
        url = '{0}/storage/backstore'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listBackStore(self, body):
        url = '{0}/storage/backstore/info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  分配给ISCSI发起者
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createAssignBackStore(self, body):
        url = '{0}/storage/backstore/assign'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  查看被分配给哪些ISCSI发起者
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listAssignBackStore(self, body):
        url = '{0}/storage/backstore/assign'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取可创建 块 的 盘 的 路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listBackStoreAvailablePath(self, body):
        url = '{0}/storage/backstore/available_path'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取版本信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeIscsiVersion(self, body):
        url = '{0}/storage/iscsi/version'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeIscsiAuth(self, body):
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  设置发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiDiscoverAuth(self, body):
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  取消发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiDiscoverAuth(self, body):
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  全局参数设置：自动添加 ISCSI目标端 门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createAutoAddPortal(self, body):
        url = '{0}/storage/iscsi/auto_add_portal'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  全局参数设置：自动添加 单元逻辑号映射
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createAutoAddLun(self, body):
        url = '{0}/storage/iscsi/auto_add_luns'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取全局参数：自动添加ISCSI目标端 门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeAutoAddPortal(self, body):
        url = '{0}/storage/iscsi/auto_add_portal'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取全局参数：自动添加单元逻辑映射
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeAutoAddLun(self, body):
        url = '{0}/storage/iscsi/auto_add_luns'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeIscsiTargetStatus(self, body):
        url = '{0}/storage/target/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listIscsiTarget(self, body):
        url = '{0}/storage/target/info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiTarget(self, body):
        url = '{0}/storage/target'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiTarget(self, body):
        url = '{0}/storage/target'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiInitiator(self, body):
        url = '{0}/storage/initiator'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiInitiator(self, body):
        url = '{0}/storage/initiator'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  设置连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiInitiatorConnectAuth(self, body):
        url = '{0}/storage/initiator/auth'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  添加 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiInitiatorLun(self, body):
        url = '{0}/storage/initiator/lun'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiInitiatorLun(self, body):
        url = '{0}/storage/initiator/lun'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  发现目标端
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiInitiatorDiscoverTarget(self, body):
        url = '{0}/storage/initiator/discover'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  连接目标端
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createIscsiInitiatorConnectTarget(self, body):
        url = '{0}/storage/initiator/connect'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  断开目标段连接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiInitiatorConnectTarget(self, body):
        url = '{0}/storage/initiator/connect'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取发现门户列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listIscsiInitiatorPortal(self, body):
        url = '{0}/storage/initiator/portal'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  删除发现门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteIscsiInitiatorPortal(self, body):
        url = '{0}/storage/initiator/portal'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def listTpg(self, body):
        url = '{0}/storage/tpg/info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createTpg(self, body):
        url = '{0}/storage/tpg'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteTpg(self, body):
        url = '{0}/storage/tpg'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  设置连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createTpgConnectAuth(self, body):
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  取消连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteTpgConnectAuth(self, body):
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  添加 逻辑单元（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createTpgLun(self, body):
        url = '{0}/storage/tpg/lun'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  是否开启连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def describeTpgConnectAuth(self, body):
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  删除 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteTpgLun(self, body):
        url = '{0}/storage/tpg/lun'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     *  添加 门户（Portal）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def createTpgPortal(self, body):
        url = '{0}/storage/tpg/portal'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除 门户（Portal）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
     '''

    def deleteTpgPortal(self, body):
        url = '{0}/storage/tpg/portal'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

