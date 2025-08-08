
from info2soft import config
from info2soft import https


class TimingBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 1-1 备份 准备-4 备份 获取MsSql数据源
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimingBackupMssqlSource(self, body):
        
        url = '{0}/timing/backup/mssql_source'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-1 备份 准备-1 备份/恢复 认证Oracle信息（目前未使用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyTimingBackupOracleInfo(self, body):
        
        url = '{0}/timing/backup/verify_oracle_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-1 备份 准备-2 备份/恢复 获取Oracle表空间（目前未使用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimingBackupOracleContent(self, body):
        
        url = '{0}/timing/backup/oracle_content'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-1 备份 准备-3 备份 获取Oracle脚本路径
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descibeTimingBackupOracleSriptPath(self, body):
        
        url = '{0}/timing/backup/oracle_script_path'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-1 备份 准备-5 备份 获取MsSql数据库列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingBackupMssqlDbList(self, body):
        
        url = '{0}/timing/backup/mssql_db_list'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 准备 验证oracle登录认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyTimingBackupOracleLogin(self, body):
        
        url = '{0}/timing/backup/oracle_login'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-2 备份 新建/编辑-1 备份 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTimingBackup(self, body):
        
        url = '{0}/timing/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-2 备份 新建/编辑-2 备份 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTimingBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/timing/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 1-2 备份 新建/编辑-3 备份 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyTimingBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/timing/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-1 备份 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingBackup(self, body):
        
        url = '{0}/timing/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-2 备份 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingBackupStatus(self, body):
        
        url = '{0}/timing/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-3 备份 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTimingBackup(self, body):
        
        url = '{0}/timing/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-4 备份 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startTimingBackup(self, body):
        
        url = '{0}/timing/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-4 备份 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTimingBackup(self, body):
        
        url = '{0}/timing/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1-3 备份 列表-4 备份 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startImmediateTimingBackup(self, body):
        
        url = '{0}/timing/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备份 列表 - 查看更多
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def showTimingBackupDetailInfo(self, body):
        
        url = '{0}/timing/backup/detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-4 备份 获取达梦数据库信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descibeDmDbInfo(self, body):
        
        url = '{0}/timing/backup/dm_db_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 1-5 备份 获取GaussDB库/表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGaussDBDatabaseTables(self, body):
        
        url = '{0}/timing/backup/list_gaussdb_database_tables'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 获取备份点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingBackupPoint(self, body):
        
        url = '{0}/timing/backup/bkup_point_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备份 - 删除备份时间点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTimingBackupPoint(self, body):
        
        url = '{0}/timing/backup/bkup_point'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 手动归档 - 获取备份时间点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakVer(self, body):
        
        url = '{0}/timing/backup/bak_ver_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 手动归档
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def bakDataArchive(self, body):
        
        url = '{0}/timing/backup/bak_data_archive'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * GoldenDB 查询实例信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeGoldebDBInfo(self, body):
        
        url = '{0}/timing/backup/goldendb_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * GoldenDB 校验实例
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyGoldebDB(self, body):
        
        url = '{0}/timing/backup/goldendb_verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取自定义数据类型
     * 
     * @return list
    '''
    def listCustomTypes(self, body):
        
        url = '{0}/timing/backup/custom_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 3-1 作业任务 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingWork(self, body):
        
        url = '{0}/timing/work'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3-2 作业任务 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTimingWork(self, body):
        
        url = '{0}/timing/work'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

