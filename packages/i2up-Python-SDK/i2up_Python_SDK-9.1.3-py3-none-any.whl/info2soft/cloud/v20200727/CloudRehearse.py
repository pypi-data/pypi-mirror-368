
from info2soft import config
from info2soft import https


class CloudRehearse (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  获取云主机信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeEcs(self, body):
        
        url = '{0}/cloud/ecs/ecs_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-主机列表
     * 
     * @return list
    '''
    def listHost(self, body):
        
        url = '{0}/cloud/rehearse/host_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-云主机列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEcs(self, body):
        
        url = '{0}/cloud/rehearse/ecs_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-恢复点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecoveryPoint(self, body):
        
        url = '{0}/cloud/rehearse/rc_point_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-区域可用区
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAvailabilityZone(self, body):
        
        url = '{0}/cloud/rehearse/availability_zone'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-规格列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFlavor(self, body):
        
        url = '{0}/cloud/rehearse/flavor_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-虚拟私有云列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpc(self, body):
        
        url = '{0}/cloud/rehearse/vpc_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-虚拟子网列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSubnet(self, body):
        
        url = '{0}/cloud/rehearse/subnet_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 准备-安全组列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecureGroup(self, body):
        
        url = '{0}/cloud/rehearse/secure_group_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  新建 - 批量
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 列表-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseStatus(self, body):
        
        url = '{0}/cloud/rehearse/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  列表 - 远程登陆
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVncConsole(self, body):
        
        url = '{0}/cloud/rehearse/vnc_console'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def evacuateRehearse(self, body):
        
        url = '{0}/cloud/rehearse/evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  批量撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def evacuateBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch_evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 演练详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseDetail(self, body):
        
        url = '{0}/cloud/rehearse/detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
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
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRehearse(self, body):
        
        url = '{0}/cloud/rehearse'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 演练历史（被撤销的演练列表）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEvacuatedRehearse(self, body):
        
        url = '{0}/cloud/rehearse/evacuated_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态 - 底层上传
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listNpsvrRehearseStatus(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/{1}/status'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  进度 - 底层上传
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listNpsvrRehearseProgress(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/rehearse/{1}/progress'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     *  演练网络配置 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNetwork(self, body):
        
        url = '{0}/cloud/rehearse/network_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  演练网络配置 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createNetwork(self, body):
        
        url = '{0}/cloud/rehearse/network_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  子网下已使用的ip列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSubnetUsedIp(self, body):
        
        url = '{0}/cloud/rehearse/subnet_used_ip_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  组演练 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createGroup(self, body):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  组演练 - 列表
     * 
     * @return list
    '''
    def listGroup(self, body):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  组演练 - 单个
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
     *  组演练 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteGroup(self, body):
        
        url = '{0}/cloud/rehearse/group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  组演练 - 撤销
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createEvacuateGroup(self, body):
        
        url = '{0}/cloud/rehearse/group_evacuate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  组演练 - 列表状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGroupStatus(self, body):
        
        url = '{0}/cloud/rehearse/group_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  组演练 - 历史列表
     * 
     * @return list
    '''
    def listEvacuatedGroup(self, body):
        
        url = '{0}/cloud/rehearse/evacuated_group_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  批量获取演练信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBatchRehearse(self, body):
        
        url = '{0}/cloud/rehearse/batch'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

