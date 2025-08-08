
from info2soft import config
from info2soft import https


class CloudBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 云平台 - 准备 - 获取区域列表（从配置文件）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCloudPlatformRegion(self, body):
        
        url = '{0}/cloud/platform/region_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 注册
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云平台 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCloudPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 云平台 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云平台 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCloudPlatformStatus(self, body):
        
        url = '{0}/cloud/platform/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCloudPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云平台 - 同步云主机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncEcs(self, body):
        
        url = '{0}/cloud/platform/sync_ecs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云平台 - 同步云硬盘
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncVolume(self, body):
        
        url = '{0}/cloud/platform/sync_volume'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云平台 - 获取规格列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFlavor(self, body):
        
        url = '{0}/cloud/platform/flavor_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 获取关联节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRelativeNode(self, body):
        
        url = '{0}/cloud/platform/node_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 切换维护
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchMaintenance(self, body):
        
        url = '{0}/cloud/platform/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云平台 - 获取区域列表（从Npsvr）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRegions(self, body):
        
        url = '{0}/cloud/platform/regions'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云平台 - 获取项目列表（从Npsvr）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listProjects(self, body):
        
        url = '{0}/cloud/platform/projects'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 准备 - 获取可用区
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listZone(self, body):
        
        url = '{0}/cloud/volume/zone_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 挂载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVolume(self, body):
        
        url = '{0}/cloud/volume/attach'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 卸载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def detachVolume(self, body):
        
        url = '{0}/cloud/volume/detach'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 状态
     * 
     * @return list
    '''
    def listVolumeStatus(self, ):
        
        url = '{0}/cloud/volume/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云硬盘 - 查询镜像列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listImage(self, body):
        
        url = '{0}/cloud/volume/image_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云硬盘 - 挂载 获取同一可用区云主机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolumeEcs(self, body):
        
        url = '{0}/cloud/volume/ecs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createEcs(self, body):
        
        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 列表 - 远程登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVncConsole(self, body):
        
        url = '{0}/cloud/ecs/vnc_console'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEcsStatus(self, body):
        
        url = '{0}/cloud/ecs/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEcs(self, body):
        
        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteEcs(self, body):
        
        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云主机 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startECS(self, body):
        
        url = '{0}/cloud/ecs/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 获取公网私网IP等信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getTakeoverECSInfo(self, body):
        
        url = '{0}/cloud/ecs/takeover_ecs_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 获取空闲挂载点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def attachPoint(self, body):
        
        url = '{0}/cloud/ecs/attach_point'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 配置演练
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def configRehearse(self, body):
        
        url = '{0}/cloud/ecs/rehearse_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 演练组 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 演练组 - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 演练组 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云主机 - 演练组 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRehearseGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/ecs/rehearse_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份 - 准备 - 工作机获取设备列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDevice(self, body):
        
        url = '{0}/cloud/ecs/device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 准备  备机获取可用云硬盘列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIdleDevice(self, body):
        
        url = '{0}/cloud/ecs/idle_device_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackup(self, body):
        
        url = '{0}/cloud/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def modifyBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, None, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCloudBackup(self, body):
        
        url = '{0}/cloud/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackup(self, body):
        
        url = '{0}/cloud/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机复制 源端virtio驱动检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifySourceVirtioDriver(self, body):
        
        url = '{0}/cloud/backup/verify_source_virtio_driver'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端拉起 - 获取云主机信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeEcs(self, body):
        
        url = '{0}/cloud/ecs/ecs_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-主机列表
     * 
     * @return list
    '''
    def listHost(self, ):
        
        url = '{0}/cloud/rehearse/host_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云端演练-准备-云主机列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEcs(self, body):
        
        url = '{0}/cloud/rehearse/ecs_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-恢复点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecoveryPoint(self, body):
        
        url = '{0}/cloud/rehearse/rc_point_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-区域可用区
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAvailabilityZone(self, body):
        
        url = '{0}/cloud/rehearse/availability_zone'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-规格列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFlavor(self, body):
        
        url = '{0}/cloud/rehearse/flavor_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-虚拟私有云列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpc(self, body):
        
        url = '{0}/cloud/rehearse/vpc_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-虚拟子网列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSubnet(self, body):
        
        url = '{0}/cloud/rehearse/subnet_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-安全组列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecureGroup(self, body):
        
        url = '{0}/cloud/rehearse/secure_group_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练 - 新建 - 批量
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练-列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-列表-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseStatus(self, body):
        
        url = '{0}/cloud/rehearse/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练 - 列表 - 远程登陆
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVncConsole(self, body):
        
        url = '{0}/cloud/rehearse/vnc_console'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def evacuateRehearse(self, body):
        
        url = '{0}/cloud/rehearse/evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练 - 批量撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def evacuateBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch_evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练-演练详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseDetail(self, body):
        
        url = '{0}/cloud/rehearse/detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRehearse(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云端演练-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云端演练-演练历史（被撤销的演练列表）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEvacuatedRehearse(self, body):
        
        url = '{0}/cloud/rehearse/evacuated_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练 - 状态 - 底层上传
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listNpsvrRehearseStatus(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/{1}/status'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, None, self.auth)
        return res

    '''
     * 云端演练 - 进度 - 底层上传
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listNpsvrRehearseProgress(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/{1}/progress'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, None, self.auth)
        return res

    '''
     * 云端演练 - 演练网络配置 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNetwork(self, body):
        
        url = '{0}/cloud/rehearse/network_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练 - 演练网络配置 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNetwork(self, body):
        
        url = '{0}/cloud/rehearse/network_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练 - 子网下已使用的ip列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSubnetUsedIp(self, body):
        
        url = '{0}/cloud/rehearse/subnet_used_ip_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createGroup(self, body):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 列表
     * 
     * @return list
    '''
    def listGroup(self, ):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteGroup(self, body):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createEvacuateGroup(self, body):
        
        url = '{0}/cloud/rehearse/group_evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 列表状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGroupStatus(self, body):
        
        url = '{0}/cloud/rehearse/group_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练 - 组演练 - 历史列表
     * 
     * @return list
    '''
    def listEvacuatedGroup(self, ):
        
        url = '{0}/cloud/rehearse/evacuated_group_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 云端演练 - 批量获取演练信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云端演练-准备-规格属性
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeFlavor(self, body):
        
        url = '{0}/cloud/rehearse/flavor_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

