
from info2soft import config
from info2soft import https


class Storage (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 存储节点 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStorageConfig(self, body):
        
        url = '{0}/storage'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储节点 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStorageConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 存储节点 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeStorageConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 存储节点 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageConfig(self, body):
        
        url = '{0}/storage'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储节点 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStorageConfig(self, body):
        
        url = '{0}/storage'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 存储节点 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageStatus(self, body):
        
        url = '{0}/storage/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储节点 - 上传设备信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadDeviceInfo(self, body):
        
        url = '{0}/storage/device_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储节点 - 获取设备信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeStorageDeviceInfo(self, body):
        
        url = '{0}/storage/device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储节点 - 获取曲线图
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeStorageHistoryData(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}/chart'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储节点 - 获取容量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStorageInfo(self, body):
        
        url = '{0}/storage/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储节点 - 获取可用节点列表
     * 
     * @return list
    '''
    def listAvailableNode(self, body):
        
        url = '{0}/storage/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 配额  - 修改开关值
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchStorageQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}/switch'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 配额 - 新建
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStorageQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}/quota'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配额  - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStorageQuota(self, body, uuid1, uuid2):
        if uuid1 is None or uuid2 is None:
            exit()
        url = '{0}/storage/{1}/quota/{2}'.format(config.get_default('default_api_host'), uuid1, uuid2)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 配额  - 获取列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listStorageQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}/quota'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 配额  - 删除
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStorageQuota(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/storage/{1}/quota'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 设备 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDevice(self, body):
        
        url = '{0}/storage/dev'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 设备 - 获取可用列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAvailableDevice(self, body):
        
        url = '{0}/storage/available_dev'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储池 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createPool(self, body):
        
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储池 - 扩展
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def expandPool(self, body):
        
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 存储池 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deletePool(self, body):
        
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 存储池 - 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPool(self, body):
        
        url = '{0}/storage/pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 存储池 - 获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPoolInfo(self, body):
        
        url = '{0}/storage/pool/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 通过节点rpc来获取池列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPoolFromNode(self, body):
        
        url = '{0}/storage/pool_from_node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件系统 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFs(self, body):
        
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件系统 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFs(self, body):
        
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 文件系统 - 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFs(self, body):
        
        url = '{0}/storage/file_system'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFsSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFsSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 - 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFsSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 / 克隆 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFsCloneSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 / 克隆 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFsCloneSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 文件系统 / 快照 / 克隆 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFsCloneSnapshot(self, body):
        
        url = '{0}/storage/file_system/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 卷 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVolume(self, body):
        
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 卷 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolume(self, body):
        
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 卷 - 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolume(self, body):
        
        url = '{0}/storage/volume'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVolumeSnapshot(self, body):
        
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolumeSnapshot(self, body):
        
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 - 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolumeSnapshot(self, body):
        
        url = '{0}/storage/volume/snap'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 / 克隆 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVolumeCloneSnapshot(self, body):
        
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 / 克隆 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolumeCloneSnapshot(self, body):
        
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 卷 / 快照 / 克隆 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolumeCloneSnapshot(self, body):
        
        url = '{0}/storage/volume/snap/clone'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * VMDK - 创建
     * 
     * @return list
    '''
    def createVMDK(self, body):
        
        url = '{0}/storage/vmdk'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * VMDK - 删除
     * 
     * @return list
    '''
    def deleteVMDK(self, body):
        
        url = '{0}/storage/vmdk'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackStore(self, body):
        
        url = '{0}/storage/backstore'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackStore(self, body):
        
        url = '{0}/storage/backstore'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackStore(self, body):
        
        url = '{0}/storage/backstore/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 分配给ISCSI发起者
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAssignBackStore(self, body):
        
        url = '{0}/storage/backstore/assign'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 查看被分配给哪些ISCSI发起者
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAssignBackStore(self, body):
        
        url = '{0}/storage/backstore/assign'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 后备存储（BackStore） - 获取可创建 块 的 盘 的 路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackStoreAvailablePath(self, body):
        
        url = '{0}/storage/backstore/available_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI - 获取版本信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeIscsiVersion(self, body):
        
        url = '{0}/storage/iscsi/version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI - 获取发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeIscsiAuth(self, body):
        
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI - 设置发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiDiscoverAuth(self, body):
        
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI - 取消发现权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiDiscoverAuth(self, body):
        
        url = '{0}/storage/iscsi/auth'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI - 全局参数设置：自动添加 ISCSI目标端 门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAutoAddPortal(self, body):
        
        url = '{0}/storage/iscsi/auto_add_portal'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI - 全局参数设置：自动添加 单元逻辑号映射
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAutoAddLun(self, body):
        
        url = '{0}/storage/iscsi/auto_add_luns'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI - 获取全局参数：自动添加ISCSI目标端 门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeAutoAddPortal(self, body):
        
        url = '{0}/storage/iscsi/auto_add_portal'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI - 获取全局参数：自动添加单元逻辑映射
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeAutoAddLun(self, body):
        
        url = '{0}/storage/iscsi/auto_add_luns'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI目标端 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeIscsiTargetStatus(self, body):
        
        url = '{0}/storage/target/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI目标端 - 获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIscsiTarget(self, body):
        
        url = '{0}/storage/target/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI目标端 - 添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiTarget(self, body):
        
        url = '{0}/storage/target'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI目标端 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiTarget(self, body):
        
        url = '{0}/storage/target'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI目标端 - 获取目标端列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIscsiTargetList(self, body):
        
        url = '{0}/storage/target_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiInitiator(self, body):
        
        url = '{0}/storage/initiator'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiInitiator(self, body):
        
        url = '{0}/storage/initiator'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 设置连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiInitiatorConnectAuth(self, body):
        
        url = '{0}/storage/initiator/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 添加 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiInitiatorLun(self, body):
        
        url = '{0}/storage/initiator/lun'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 删除 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiInitiatorLun(self, body):
        
        url = '{0}/storage/initiator/lun'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 发现目标端
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiInitiatorDiscoverTarget(self, body):
        
        url = '{0}/storage/initiator/discover'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 连接目标端
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createIscsiInitiatorConnectTarget(self, body):
        
        url = '{0}/storage/initiator/connect'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 断开目标段连接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiInitiatorConnectTarget(self, body):
        
        url = '{0}/storage/initiator/connect'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 获取发现门户列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIscsiInitiatorPortal(self, body):
        
        url = '{0}/storage/initiator/portal'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 删除发现门户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIscsiInitiatorPortal(self, body):
        
        url = '{0}/storage/initiator/portal'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 刷新会话
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def iscsiInitiatorRefreshSession(self, body):
        
        url = '{0}/storage/initiator/refresh_session'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 获取信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTpg(self, body):
        
        url = '{0}/storage/tpg/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTpg(self, body):
        
        url = '{0}/storage/tpg'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTpg(self, body):
        
        url = '{0}/storage/tpg'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 设置连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTpgConnectAuth(self, body):
        
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 取消连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTpgConnectAuth(self, body):
        
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 添加 逻辑单元（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTpgLun(self, body):
        
        url = '{0}/storage/tpg/lun'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG）- 是否开启连接权限
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTpgConnectAuth(self, body):
        
        url = '{0}/storage/tpg/auth'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 删除 逻辑单元号（LUN）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTpgLun(self, body):
        
        url = '{0}/storage/tpg/lun'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 添加 门户（Portal）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTpgPortal(self, body):
        
        url = '{0}/storage/tpg/portal'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 目标门户组（TPG） - 删除 门户（Portal）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTpgPortal(self, body):
        
        url = '{0}/storage/tpg/portal'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * Server是否注册
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerServer(self, body):
        
        url = '{0}/storage/server_register'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTape(self, body):
        
        url = '{0}/tape'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 扫描
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanTapes(self, body):
        
        url = '{0}/tape/scan_tapes'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTape(self, body):
        
        url = '{0}/tape'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTape(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 磁带库 - 更新
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyTape(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 磁带库 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTape(self, body):
        
        url = '{0}/tape'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def eraseTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def formatTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def browseTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebuildCatalogTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def catalogTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def unloadTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updatePoolsTape(self, body):
        
        url = '{0}/tape/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - slot：获取备份数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBkData(self, body):
        
        url = '{0}/tape/bkdata_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 查看备份数据下的详细文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBkFile(self, body):
        
        url = '{0}/tape/bkfile_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取有磁带的驱动索引
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBusyDrive(self, body):
        
        url = '{0}/tape/busy_drive_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取没有磁带的空闲槽
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFreeSlot(self, body):
        
        url = '{0}/tape/free_slot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取有磁带的IE槽
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBusyIEslot(self, body):
        
        url = '{0}/tape/busy_ieslot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取空闲的IE Slot
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFreeIEslot(self, body):
        
        url = '{0}/tape/free_ieslot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取有磁带的Slot
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBusySlot(self, body):
        
        url = '{0}/tape/busy_slot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 查看磁带详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def discribeTapeDetail(self, body):
        
        url = '{0}/tape/details'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带池 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapePools(self, body):
        
        url = '{0}/tape_pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带池 - 获取磁带列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapePoolSlots(self, body):
        
        url = '{0}/tape_pool/list_slots'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带池 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTapePool(self, body):
        
        url = '{0}/tape_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addSlotTapePool(self, body):
        
        url = '{0}/tape_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def removeSlotTapePool(self, body):
        
        url = '{0}/tape_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTapePool(self, body):
        
        url = '{0}/tape_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateTapePool(self, body):
        
        url = '{0}/tape_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带池 - 获取磁带名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeNames(self, body):
        
        url = '{0}/tape_pool/tape_names'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

