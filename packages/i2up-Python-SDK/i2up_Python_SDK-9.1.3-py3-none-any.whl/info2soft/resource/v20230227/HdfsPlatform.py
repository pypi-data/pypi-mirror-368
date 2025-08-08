
from info2soft import config
from info2soft import https


class HdfsPlatform (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHdfsPlatform(self, body):
        
        url = '{0}/hdfs_platform'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHdfsPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs_platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsPlatform(self, body):
        
        url = '{0}/hdfs_platform'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHdfsPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs_platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHdfsPlatform(self, body):
        
        url = '{0}/hdfs_platform'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取同步路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsPath(self, body):
        
        url = '{0}/hdfs_platform/hdfs_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取hive资源（数据库，表）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsHiveEntity(self, body):
        
        url = '{0}/hdfs_platform/hive_entity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

