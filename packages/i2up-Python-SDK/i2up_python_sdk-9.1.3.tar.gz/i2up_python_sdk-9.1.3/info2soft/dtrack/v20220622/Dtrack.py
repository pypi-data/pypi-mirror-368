
from info2soft import config
from info2soft import https


class Dtrack (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取工作机设备列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackBackupDev(self, body):
        
        url = '{0}/dtrack/backup/dev'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查询工作机系统信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackBackupSystemInfo(self, body):
        
        url = '{0}/dtrack/backup/system_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略 - 检查是否重名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyDtrackBackupName(self, body):
        
        url = '{0}/dtrack/backup/verify_name'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtrackBackup(self, body):
        
        url = '{0}/dtrack/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtrackBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 策略 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtrackBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 策略 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackBackup(self, body):
        
        url = '{0}/dtrack/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackBackupStatus(self, body):
        
        url = '{0}/dtrack/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtrackBackup(self, body):
        
        url = '{0}/dtrack/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 创建快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def takeSnapshotDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'take_snapshot'
            }
        else:
            body['operate'] = 'take_snapshot'
        
        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 删除快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSnapshotDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'delete_snapshot'
            }
        else:
            body['operate'] = 'delete_snapshot'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 创建克隆
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def takeSnapshotCloneDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'take_snapshot_clone'
            }
        else:
            body['operate'] = 'take_snapshot_clone'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 删除克隆
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSnapshotCloneDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'delete_snapshot_clone'
            }
        else:
            body['operate'] = 'delete_snapshot_clone'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'scan'
            }
        else:
            body['operate'] = 'scan'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 取消分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cancelScanDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'cancel_scan'
            }
        else:
            body['operate'] = 'cancel_scan'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 同步
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'sync'
            }
        else:
            body['operate'] = 'sync'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 取消同步
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cancelSyncDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'cancel_sync'
            }
        else:
            body['operate'] = 'cancel_sync'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 暂停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def suspendDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'suspend'
            }
        else:
            body['operate'] = 'suspend'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeDtrackBackup(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/dtrack/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 添加历史记录（底层调）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addDtrackBackupHistory(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}/history'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 查询历史记录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackBackupHistory(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}/history'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略 - 获取快照列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listDtrackBackupSnap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}/snap'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 安装卸载驱动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dtrackBackupCtlDrv(self, body):
        
        url = '{0}/dtrack/backup/ctl_drv'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 重启系统
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dtrackBackupRebootSystem(self, body):
        
        url = '{0}/dtrack/backup/reboot'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略 - 获取服务功能
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dtrackBackupFeatureMatrix(self, body):
        
        url = '{0}/dtrack/backup/feature_matrix'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 获取名称
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDtrackNodeInitiatorName(self, body):
        
        url = '{0}/dtrack/node/initiator_name'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDtrackNodeInitiatorStatus(self, body):
        
        url = '{0}/dtrack/node/initiator_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * ISCSI发起者 - 获取版本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDtrackNodeInitiatorVersion(self, body):
        
        url = '{0}/dtrack/node/initiator_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * MySQL - 配置访问参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def mysqlConf(self, body):
        
        url = '{0}/dtrack/node/mysql_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * MySQL - 获取访问参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMysqlConf(self, body):
        
        url = '{0}/dtrack/node/mysql_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * MySQL - 获取数据库名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMysqlDb(self, body):
        
        url = '{0}/dtrack/node/mysql_db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Oracle - 配置访问参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def oracleConf(self, body):
        
        url = '{0}/dtrack/node/oracle_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Oracle - 获取访问参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOracleConf(self, body):
        
        url = '{0}/dtrack/node/oracle_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Oracle - 获取表空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOracleDb(self, body):
        
        url = '{0}/dtrack/node/oracle_db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * SqlServer - 配置访问参数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def sqlserverConf(self, body):
        
        url = '{0}/dtrack/node/sqlserver_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * SqlServer - 获取访问参数副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSqlserverConf(self, body):
        
        url = '{0}/dtrack/node/sqlserver_conf'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 获取目标端列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackRecoveryTarget(self, body):
        
        url = '{0}/dtrack/recovery/target'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 还原 - 是否发现目标端
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDtrackRecoveryTargetDiscovered(self, body):
        
        url = '{0}/dtrack/recovery/target_discovered'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略组 - 创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtrackGroup(self, body):
        
        url = '{0}/dtrack/group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtrackGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 策略组 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtrackGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略组 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackGroup(self, body):
        
        url = '{0}/dtrack/group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略组 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtrackGroupStatus(self, body):
        
        url = '{0}/dtrack/group/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 策略组 - 更新绑定
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateDtrackGroupBind(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/group/{1}/bind'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 策略 - 更新绑定
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateDtrackBackupBind(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/backup/{1}/bind'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 策略组 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtrackGroup(self, body):
        
        url = '{0}/dtrack/group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 暂停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def suspendDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'suspend'
            }
        else:
            body['operate'] = 'suspend'
        
        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 同步
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'sync'
            }
        else:
            body['operate'] = 'sync'

        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 取消同步
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cancelSyncDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'cancel_sync'
            }
        else:
            body['operate'] = 'cancel_sync'

        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 创建快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def takeSnapshotDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'take_snapshot'
            }
        else:
            body['operate'] = 'take_snapshot'

        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 操作 删除快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSnapshotDtrackGroup(self, body):
        if body is None:
            body = {
                'operate': 'delete_snapshot'
            }
        else:
            body['operate'] = 'delete_snapshot'

        url = '{0}/dtrack/group/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 策略组 - 获取快照列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listDtrackGroupSnap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dtrack/group/{1}/snap'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

