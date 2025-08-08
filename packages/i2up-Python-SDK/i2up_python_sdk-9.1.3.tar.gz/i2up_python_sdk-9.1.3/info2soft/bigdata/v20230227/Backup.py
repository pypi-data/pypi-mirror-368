
from info2soft import config
from info2soft import https


class Backup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 备份 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupStatus(self, body):
        
        url = '{0}/bigdata/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备份 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 还原 - 准备 - 获取备份列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupHistory(self, body):
        
        url = '{0}/bigdata/recovery/bak_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataRecovery(self, body):
        
        url = '{0}/bigdata/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 还原 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 还原 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigdataRecovery(self, body):
        
        url = '{0}/bigdata/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 还原 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataRecovery(self, body):
        
        url = '{0}/bigdata/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataRecoveryStatus(self, body):
        
        url = '{0}/bigdata/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据平台 - 认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authBigdataPlatform(self, body):
        
        url = '{0}/bigdata/backup/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 条件获取hive数据库表名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataHiveTable(self, body):
        
        url = '{0}/bigdata/backup/hive_table_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取所有数据库
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAllBigdataHiveDatabase(self, body):
        
        url = '{0}/bigdata/backup/all_hive_database'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据 - 获取hive表详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getTableInfoDetail(self, body):
        
        url = '{0}/bigdata/recovery/table_info_detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据 - 测试链接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def testClusterConnection(self, body):
        
        url = '{0}/bigdata/backup/cluster_check'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

