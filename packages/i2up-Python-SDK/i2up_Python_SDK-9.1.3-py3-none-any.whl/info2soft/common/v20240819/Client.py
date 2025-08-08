
from info2soft import config
from info2soft import https


class Client (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取控制机IP或节点代理开关
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRestRpcCcip(self, body):
        
        url = '{0}/api/client/rest_rpc/cc_ip'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带信息更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateTapeMedia(self, body):
        
        url = '{0}/api/client/rest_rpc/tape_media'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 快速注册节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerNodeFromNode(self, body):
        
        url = '{0}/api/client/rest_rpc/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步修改从类型节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSlaveNode(self, body):
        
        url = '{0}/api/client/update_slave_node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 上报结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcresult(self, body):
        
        url = '{0}/api/client/rest_rpc/result'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Ha动态节点切换后上报接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcHa(self, body):
        
        url = '{0}/api/client/rest_rpc/ha'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 服务器池更新底层传上来的中心节点IP
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addRestRpcCluster(self, body):
        
        url = '{0}/api/client/rest_rpc/cluster'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 复制/NAS规则，创建比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCompareResult(self, body):
        
        url = '{0}/api/client/create_compare_result'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 上传比较与同步执行差异详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadCompareDiffDetail(self, body):
        
        url = '{0}/api/client/upload_diff_detail'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 上传比较与同步任务执行结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def collectCompareResult(self, body):
        
        url = '{0}/api/client/collect_compare_result'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 创建结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyEcs(self, body):
        
        url = '{0}/api/client/rest_rpc/cloud_ecs'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取所有虚拟平台
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVirtualPlatforms(self, body):
        
        url = '{0}/api/client/get_virtual_platforms'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取指定虚拟平台上的所有规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVirtualPlatformRules(self, body):
        
        url = '{0}/api/client/get_virtual_platform_rules'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取所有对象存储
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getDtoStorageList(self, body):
        
        url = '{0}/api/client/get_dto_storage_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取数据库同步规则（返回rpc下发的格式）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getAllActiveRules(self, body):
        
        url = '{0}/api/client/get_active_rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * HDFS差异比较结果上传
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadHdfsCompareResult(self, body):
        
        url = '{0}/api/client/upload_hdfs_compare_result'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * CFS - 机头迁移
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cfsNodeMove(self, body):
        
        url = '{0}/api/client/cfs_node_move'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * CFS - 机头迁移前停止规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cfsStopRule(self, body):
        
        url = '{0}/api/client/cfs_stop_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带组名 - 列表
     * 
     * @return list
    '''
    def listSlotTapeName(self, body):
        
        url = '{0}/api/client/rest_rpc/slot_tapename'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

