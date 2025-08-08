
from info2soft import config
from info2soft import https


class CloudPlatform (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  准备 - 获取区域列表
     * 
     * @return list
    '''
    def listCloudPlatformRegion(self, body):
        
        url = '{0}/cloud/platform/region_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  注册
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  修改
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
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCloudPlatform(self, body):
        
        url = '{0}/cloud/platform'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCloudPlatformStatus(self, body):

        url = '{0}/cloud/platform/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取单个
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
     *  同步云主机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncEcs(self, body):
        
        url = '{0}/cloud/platform/sync_ecs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  同步云硬盘
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncVolume(self, body):
        
        url = '{0}/cloud/platform/sync_volume'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取规格信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFlavor(self, body):
        
        url = '{0}/cloud/platform/flavor_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  获取关联节点列表
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
