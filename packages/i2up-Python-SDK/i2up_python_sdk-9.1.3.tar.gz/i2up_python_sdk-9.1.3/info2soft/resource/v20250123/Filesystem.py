
from info2soft import config
from info2soft import https


class Filesystem (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 文件系统 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFilesystem(self, body):
        
        url = '{0}/filesystem'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件系统 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFilesystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/filesystem/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 文件系统 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFilesystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/filesystem/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 文件系统 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFilesystemStatus(self, body):
        
        url = '{0}/filesystem/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件系统 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFilesystem(self, body):
        
        url = '{0}/filesystem'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 文件系统 - 列表
     * 
     * @return list
    '''
    def listFilesystem(self, body):
        
        url = '{0}/filesystem'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 文件系统 - 获取节点文件系统列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def loadFilesystemList(self, body):
        
        url = '{0}/filesystem/load_filesystem_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量导入文件系统
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importFilesystemList(self, body):
        
        url = '{0}/filesystem/batch_import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

