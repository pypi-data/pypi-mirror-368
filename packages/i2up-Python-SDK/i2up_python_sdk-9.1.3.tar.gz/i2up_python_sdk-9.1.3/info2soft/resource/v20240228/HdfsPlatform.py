
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

    '''
     * 备份主机 - 认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authBigdataBackupHost(self, body):
        
        url = '{0}/bigdata/backup_host/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份主机 - 数据库认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def bigdataBackupHostDbAuth(self, body):
        
        url = '{0}/bigdata/backup_host/db_auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份主机 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataBackupHost(self, body):
        
        url = '{0}/bigdata/backup_host'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份主机 - 列表
     * 
     * @return list
    '''
    def listBigdataBackupHost(self, body):
        
        url = '{0}/bigdata/backup_host'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份主机 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataBackupHost(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/backup_host/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份主机 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBigdataBackupHost(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/backup_host/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 备份主机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigdataBackupHost(self, body):
        
        url = '{0}/bigdata/backup_host'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备份主机 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupHoststatus(self, body):
        
        url = '{0}/bigdata/backup_host/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据平台 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataPlatform(self, body):
        
        url = '{0}/bigdata/platform'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据平台 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 大数据平台 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBigdataPlatform(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/platform/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 大数据平台 - 列表
     * 
     * @return list
    '''
    def listBigdataPlatform(self, body):
        
        url = '{0}/bigdata/platform'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 大数据平台 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigdataPlatform(self, body):
        
        url = '{0}/bigdata/platform'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 大数据平台 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataPlatformStatus(self, body):
        
        url = '{0}/bigdata/platform/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

