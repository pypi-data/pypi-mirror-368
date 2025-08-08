
from info2soft import config
from info2soft import https


class AppHighAvailability (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * Dashboard - 高可用列表
     * 
     * @return list
    '''
    def ha(self, body):
        
        url = '{0}/dashboard/ha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Dashboard - 高可用列表副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    # def ha(self, body):
    #
    #     url = '{0}7.1.28/dashboard/ha'.format(config.get_default('default_api_host'))
    #
    #     res = https._get(url, body, self.auth)
    #     return res

    '''
     * 高可用 - 节点网卡信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNicInfo(self, body):
        
        url = '{0}/ha/netif'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用 - HA脚本目录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeHAScriptPath(self, body):
        
        url = '{0}ha/script_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用 - 磁盘信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVolumeInfo(self, body):
        
        url = '{0}ha/volume_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用 - 检查是否重名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def haVerifyName(self, body):
        
        url = '{0}/ha/verify_name'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高可用 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHA(self, body):
        
        url = '{0}/ha'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高可用 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHA(self, body):
        
        url = '{0}ha'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 高可用 - 查看详细信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHA(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}ha/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 高可用 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHA(self, body):
        
        url = '{0}/ha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHAStatus(self, body):
        
        url = '{0}/ha/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高可用 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startHA(self, body):
        
        url = '{0}/ha/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高可用 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHA(self, body):
        
        url = '{0}ha'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 高可用组 - 阶段选项
     * 
     * @return list
    '''
    def listStageOptions(self, body):
        
        url = '{0}/ha/group/stage_options'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 高可用组-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHAGroup(self, body):
        
        url = '{0}/ha/group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高可用组 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHAGroup(self, body):
        
        url = '{0}/ha/group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用组 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHAGroup(self, body):
        
        url = '{0}/ha/group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 高可用组 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHAGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 高可用组 - 单个详细信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHAGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 高可用组 - 组强制切换
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def forceSwitchHAGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/group/{1}/task'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 高可用组 - 切换状态
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHASwitchTaskStatus(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/group/{1}/task/status'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高可用组 - 操作强制切换任务
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeHAGroupSwitch(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/group/{1}/task'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

