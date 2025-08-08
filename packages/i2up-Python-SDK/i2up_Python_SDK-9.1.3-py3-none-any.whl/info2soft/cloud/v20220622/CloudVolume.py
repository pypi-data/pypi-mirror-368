
from info2soft import config
from info2soft import https


class CloudVolume (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  准备 - 获取可用区
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listZone(self, body):
        
        url = '{0}/cloud/volume/zone_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  挂载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVolume(self, body):
        
        url = '{0}/cloud/volume/attach'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  卸载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def detachVolume(self, body):
        
        url = '{0}/cloud/volume/detach'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolume(self, body):
        
        url = '{0}/cloud/volume'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @return list
    '''
    def listVolumeStatus(self, body):
        
        url = '{0}/cloud/volume/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  查询镜像列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listImage(self, body):
        
        url = '{0}/cloud/volume/image_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  挂载 获取同一可用区云主机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVolumeEcs(self, body):
        
        url = '{0}/cloud/volume/ecs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res
