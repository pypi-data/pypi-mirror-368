
from info2soft import config
from info2soft import https


class CloudBackup (object):
    def __init__(self, auth):
        self.auth = auth
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
        
        res = https._put(url, body, self.auth)
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
     * 备份(云容灾-整机复制) - 启停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startBackup(self, body):
        
        url = '{0}/cloud/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 启停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBackup(self, body):
        
        url = '{0}/cloud/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份(云容灾-整机复制) - 启停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startImmediatelyBackup(self, body):
        
        url = '{0}/cloud/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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

