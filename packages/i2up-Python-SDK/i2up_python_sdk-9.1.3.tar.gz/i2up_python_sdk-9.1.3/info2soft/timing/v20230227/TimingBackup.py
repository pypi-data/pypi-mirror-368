
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
     * 2-1 恢复 准备-2 恢复 获取还原时间点 - Mssql
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryMssqlTime(self, body):
        
        url = '{0}/timing/recovery/rc_mssql_time'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-1 恢复 准备-3 恢复 获取Mssql初始信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimingRecoveryMssqlInitInfo(self, body):
        
        url = '{0}/timing/recovery/rc_mssql_init_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-1 恢复 准备-1 恢复 获取还原时间点 - 文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryPathList(self, body):
        
        url = '{0}/timing/recovery/rc_path_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-1 恢复 准备-4 恢复 认证MsSql数据库
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyTimingRecoveryMssqlInfo(self, body):
        
        url = '{0}/timing/recovery/rc_verify_mssql_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复 准备 获取oracle恢复点日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryOracleRcPointInfo(self, body):
        
        url = '{0}/timing/recovery/rc_sbt'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 准备 获取MySQL备份目录信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRcMysqlInfo(self, body):
        
        url = '{0}/timing/recovery/rc_mysql_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 获取控制文件参数文件列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSbtContrlFile(self, body):
        
        url = '{0}/timing/recovery/sbt_contrlfile'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 获取DBID
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSbtDbid(self, body):
        
        url = '{0}/timing/recovery/sbt_dbid'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-2 恢复 新建/编辑-1 恢复 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTimingRecovery(self, body):
        
        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2-2 恢复 新建/编辑-3 恢复 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyTimingRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/timing/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 2-2 恢复 新建/编辑-2 恢复 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTimingRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/timing/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 2-3 恢复 列表-1 恢复 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecovery(self, body):
        
        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-3 恢复 列表-3 恢复 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTimingRecovery(self, body):
        
        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 2-3 恢复 列表-2 恢复 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryStatus(self, body):
        
        url = '{0}/timing/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2-3 恢复 列表-4 恢复 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startTimingRecovery(self, body):
        
        url = '{0}/timing/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2-4 恢复 mssql 获取单个组
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeGroupTimingRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/timing/recovery/{1}/group'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 恢复 检查 目录是否存在
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def timingRecoveryCheckDir(self, body):
        
        url = '{0}/timing/recovery/check_dir'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2-5 恢复 多库备份获取数据库列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryDbInfo(self, body):
        
        url = '{0}/timing/recovery/db_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 - 准备1 - DB2获取时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryDb2Time(self, body):
        
        url = '{0}/timing/recovery/rc_db2_time'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 获取GAUSS还原时间点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryGaussTime(self, body):
        
        url = '{0}/timing/recovery/gaussdb_rc_time'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 达梦 获取备份集信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTimingRecoveryDmBackupInfo(self, body):
        
        url = '{0}/timing/recovery/dm_backup_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 临时挂载复制卷
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateVolume(self, body):
        
        url = '{0}/timing/recovery/volume_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
     * 文件还原 - 挂载路径动作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def taskMountDir(self, body):
        
        url = '{0}/timing/recovery/task_mount_dir'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 合成恢复获取还原时间点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFileSnapshot(self, body):
        
        url = '{0}/timing/recovery/file_snapshot_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 合成恢复获取备份点数据库详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbNames(self, body):
        
        url = '{0}/timing/recovery/db_names'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
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

