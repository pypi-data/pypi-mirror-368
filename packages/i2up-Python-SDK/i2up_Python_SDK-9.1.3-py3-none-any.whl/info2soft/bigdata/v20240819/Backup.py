
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
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startImmediatelyBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def disableBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def pauseBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
     * 备份 - 查看冷数据 -  建表语句
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupTableDdl(self, body):
        
        url = '{0}/bigdata/backup/table_ddl'.format(config.get_default('default_api_host'))
        
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
     * 大数据 - 获取hive库中相应表的区名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getBigdataBackupPartitions(self, body):
        
        url = '{0}/bigdata/backup/partitions'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup/import'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

