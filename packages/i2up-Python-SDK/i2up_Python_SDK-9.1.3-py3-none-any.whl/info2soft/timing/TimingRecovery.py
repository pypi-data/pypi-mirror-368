from info2soft import config
from info2soft import https


class TimingRecovery(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 1 恢复 准备-2 恢复 获取还原时间点 - Mssql
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listTimingRecoveryDb2Time(self, body):

        url = '{0}/timing/recovery/rc_db2_time'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 恢复 准备-2 恢复 获取还原时间点 - Mssql
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listTimingRecoveryMssqlTime(self, body):

        url = '{0}/timing/recovery/rc_mssql_time'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 恢复 准备-3 恢复 获取Mssql初始信息
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def describeTimingRecoveryMssqlInitInfo(self, body):

        url = '{0}/timing/recovery/rc_mssql_init_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 恢复 准备-1 恢复 获取还原时间点 - 文件
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listTimingRecoveryPathList(self, body):

        url = '{0}/timing/recovery/rc_path_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 恢复 准备-4 恢复 认证MsSql数据库
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def verifyTimingRecoveryMssqlInfo(self, body):

        url = '{0}/timing/recovery/rc_verify_mssql_info'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * ------------------------- 分隔线 --------------------------
     * 
     * @return array
     '''

    '''
     * 2 恢复 新建/编辑-1 恢复 新建
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def createTimingRecovery(self, body):

        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 恢复 新建/编辑-3 恢复 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def modifyTimingRecovery(self, body):

        url = '{0}/timing/recovery/{1}'.format(config.get_default('default_api_host'), body['timing_recovery']['task_uuid'])

        res = https._put(url, body, self.auth)
        return res

    '''
     * 2 恢复 新建/编辑-2 恢复 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''

    def describeTimingRecovery(self, body):
        if body is None or 'task_uuid' not in body:
            exit()
        url = '{0}/timing/recovery/{1}'.format(config.get_default('default_api_host'), body['task_uuid'])

        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 恢复 列表-1 恢复 获取列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listTimingRecovery(self, body):

        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 3 恢复 列表-2 恢复 状态
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listTimingRecoveryStatus(self, body):

        url = '{0}/timing/recovery/status'.format(config.get_default('default_api_host'))
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3 恢复 列表-3 恢复 删除
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def deleteTimingRecovery(self, body):

        url = '{0}/timing/recovery'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 3 恢复 列表-4 恢复 操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def startTimingRecovery(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        url = '{0}/timing/recovery/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    def stopTimingRecovery(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'
        url = '{0}/timing/recovery/operate'.format(config.get_default('default_api_host'))

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
     * 恢复 - 准备1 - DB2获取时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryDb(self, body):

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
