
from info2soft import config
from info2soft import https


class VirtualizationSupport (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 虚拟平台 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVp(self, body):
        
        url = '{0}/vp/platform'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚拟平台 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVp(self, body):
        
        url = '{0}/vp/platform'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpStatus(self, body):
        
        url = '{0}/vp/platform/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateDataAgentVp(self, body):
        
        url = '{0}/vp/platform/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVp(self, body):
        
        url = '{0}/vp/platform'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 虚机列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVM(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/vm'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取不带层级结构的虚机列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmNoHierarchy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/vm_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 单个虚机的详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmInfo(self, body):
        
        url = '{0}/vp/platform/vm_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 平台属性
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpAttribute(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/info'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚拟平台 - 查 备机上备份列表（RC）1
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakVer(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/bak_ver'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 备份点信息（RC）2
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakVerInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/bak_ver_info'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 数据存储下文件列表（RC）3
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatastoreFile(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datastore_file'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 数据中心列表（MOVE/REP）1
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listDatacenter(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datacenter'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚拟平台 - 查 数据中心主机列表 （MOVE/REP）2
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatacenterHost(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datacenter_host'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 存储列表 （MOVE/REP/RC）3
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatastore(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datastore'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 存储信息 （MOVE/REP/RC）4
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatastoreInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datastore_info'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 创建存储目录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDatastore(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/datastore'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 虚机磁盘
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmDisk(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/vm_disk'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 查 平台网卡
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNetwork(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/network'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 演练配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def drilConfigInfo(self, body):
        
        url = '{0}/vp/platform/drill_config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 -导入虚机 IP映射，模板下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dl(self, body):
        
        url = '{0}/dl'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 导入虚机 IP映射
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importVmIpMapping(self, body):
        
        url = '{0}/vp/platform/batch_vm_ip_mapping'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 获取虚机网卡信息列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNetworkInfo(self, body):
        
        url = '{0}/vp/platform/network_info_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 获取指定操作系统的信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeOsVersion(self, body):
        
        url = '{0}/vp/platform/os_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚拟平台 - 获取安全组
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecurityGroup(self, body):
        
        url = '{0}/vp/platform/security_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取 虚机复制/整机备份 目标机状态信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def tgtVmStatusInfo(self, body):
        
        url = '{0}/vp/platform/tgt_vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 单个平台存储列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPlatformStorage(self, body):
        
        url = '{0}/vp/storage/platform_storage_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改存储授权容量、启用状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def platformAuthorize(self, body):
        
        url = '{0}/vp/storage/platform_authorize'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 存储列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpStorage(self, body):
        
        url = '{0}/vp/storage'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 通过ip和port，获取备份点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakVerByIp(self, body):
        
        url = '{0}/vp/platform/bk_ver_by_ip'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 通过ip和port，获取备份点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakVerInfoByIp(self, body):
        
        url = '{0}/vp/platform/bk_ver_info_by_ip'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 测试连接节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def testNode(self, body):
        
        url = '{0}/vp/platform/test_node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取规则目标机信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getTargetVmInfo(self, body):
        
        url = '{0}/vp/platform/target_vm_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取平台卷类型列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDiskType(self, body):
        
        url = '{0}/vp/platform/disk_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 发现虚机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def discoveryVm(self, body):
        
        url = '{0}/vp/platform/discovery_vm'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Winstack - 获取主机池列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listPools(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/pool_list/'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Winstack - 获取主机池主机列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listPoolHosts(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/pool_host_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * AIO - 获取集群列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listAioClusters(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/aio_cluster_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * AIO - 获取主机列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAioHosts(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/aio_host_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * AIO - 获取主机下存储池
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAioPools(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/aio_pool_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * AIO - 获取主机架构和仿真机类型
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeAioHostCapability(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/aio_host_capability'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * SCP - 获取主机列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listScpHosts(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/platform/{1}/scp_host_list'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res


