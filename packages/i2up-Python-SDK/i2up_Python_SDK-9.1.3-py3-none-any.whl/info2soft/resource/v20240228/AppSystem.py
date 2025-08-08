
from info2soft import config
from info2soft import https


class AppSystem (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取列表
     * 
     * @return list
    '''
    def secDirList(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSecDir(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySecDir(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/sec_dir/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSecDir(self, body):
        
        url = '{0}/sec_dir'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def appSystemList(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取列表（附加成员列表）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def appSystemMembersList(self, body):
        
        url = '{0}app_sys/get_app_sys_members'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeAppSystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_sys/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAppSystem(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAppSystem(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_sys/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAppSystem(self, body):
        
        url = '{0}/app_sys'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取虚机成员列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVmList(self, body):
        
        url = '{0}/app_sys/vm_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看全部成员列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getMembersList(self, body):
        
        url = '{0}/app_sys/members_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取接管列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryList(self, body):
        
        url = '{0}/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取接管规则状态（工作机、上次运行时间、回切）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryStatus(self, body):
        
        url = '{0}/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 任务列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchTaskList(self, body):
        
        url = '{0}/batch_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 任务状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchTaskStatus(self, body):
        
        url = '{0}/batch_task/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量任务 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startBatchTask(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 批量任务 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBatchTask(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 批量任务 - 操作 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBatchTask(self, body):
        if body is None:
            body = {
                'operate': 'delete'
            }
        else:
            body['operate'] = 'delete'

        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 资源概览（旧）
     * 
     * @return list
    '''
    def resourceView(self, body):
        
        url = '{0}/dashboard/source'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 资源概览 - 获取资源池列表
     * 
     * @return list
    '''
    def listBackupCenter(self, body):
        
        url = '{0}/dashboard/list_backup_center'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 资源概览 - 获取资源使用率和保护覆盖率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getBackupCenterInfo(self, body):
        
        url = '{0}/dashboard/backup_center_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源概览 - 获取接管、演练平台列表
     * 
     * @return list
    '''
    def listHosts(self, body):
        
        url = '{0}/dashboard/list_hosts'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 设置资源保护覆盖率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resourceProtectionCoverage(self, body):
        
        url = '{0}/dashboard/resource_protection_coverage'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 任务概览列表
     * 
     * @return list
    '''
    def taskView(self, body):
        
        url = '{0}/dashboard/task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatisticsReport(self, body):
        
        url = '{0}/statistics/report'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 自动注册节点（底层调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def autoRegisterNode(self, body):
        
        url = '{0}/api/client/rest_rpc/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机副本 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFullMachineCopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/full_machine_copy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 整机副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 整机副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFullMachineCopy(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/full_machine_copy/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 整机副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFullMachineCopy(self, body):
        
        url = '{0}/full_machine_copy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机副本 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFullMachineCopyStatus(self, body):

        url = '{0}/full_machine_copy/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 整机副本 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startFullMachineCopy(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/full_machine_copy/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 整机副本 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopFullMachineCopy(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/full_machine_copy/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyAppContinuity(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_continuity/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeAppContinuity(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/app_continuity/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用容灾 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAppContinuity(self, body):
        
        url = '{0}/app_continuity'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 立即快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def snapshotImmediatelyAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'snapshot_immediately'
            }
        else:
            body['operate'] = 'snapshot_immediately'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 删除快照
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def snapshotDeleteAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'snapshot_delete'
            }
        else:
            body['operate'] = 'snapshot_delete'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 接管
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failoverAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'failover'
            }
        else:
            body['operate'] = 'failover'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 回退
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def failbackAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'failback'
            }
        else:
            body['operate'] = 'failback'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 操作 脚本管理
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyScriptAppContinuity(self, body):
        if body is None:
            body = {
                'operate': 'modify_script'
            }
        else:
            body['operate'] = 'modify_script'

        url = '{0}/app_continuity/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用容灾 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAppContinuityStatus(self, body):

        url = '{0}/app_continuity/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 一级副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeFirstReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/first/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 一级副本 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyFirstReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/first/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 一级副本 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFirstReplicaStatus(self, body):
        
        url = '{0}/replica/first/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 一级副本 - 操作 开机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmFirstReplica(self, body):
        if body is None:
            body = {
                'operate': 'start_vm'
            }
        else:
            body['operate'] = 'start_vm'
        
        url = '{0}/replica/first/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 操作 开机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmFirstReplica(self, body):
        if body is None:
            body = {
                'operate': 'stop_vm'
            }
        else:
            body['operate'] = 'stop_vm'

        url = '{0}/replica/first/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 一级副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteFirstReplica(self, body):
        
        url = '{0}/replica/first'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 二级副本 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 二级副本 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeSecondReplica(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/replica/second/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 二级副本 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startSecondReplica(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        
        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSecondReplica(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmSecondReplica(self, body):
        if body is None:
            body = {
                'operate': 'start_vm'
            }
        else:
            body['operate'] = 'start_vm'

        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmSecondReplica(self, body):
        if body is None:
            body = {
                'operate': 'stop_vm'
            }
        else:
            body['operate'] = 'stop_vm'

        url = '{0}/replica/second/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 二级副本 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSecondReplica(self, body):
        
        url = '{0}/replica/second'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVmCloneRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机克隆规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVmCloneRule(self, body):
        
        url = '{0}/vm_clone/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 操作 开始
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmCloneRule(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        
        url = '{0}/vm_clone/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmCloneRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/vm_clone/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆规则 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneRuleStatus(self, body):
        
        url = '{0}/vm_clone/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneVm(self, body):
        
        url = '{0}/vm_clone/vm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 修改虚机配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVmConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/vm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 操作 开机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVmVmCloneVm(self, body):
        if body is None:
            body = {
                'operate': 'start_vm'
            }
        else:
            body['operate'] = 'start_vm'
        
        url = '{0}/vm_clone/vm/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 操作 关机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVmVmCloneVm(self, body):
        if body is None:
            body = {
                'operate': 'stop_vm'
            }
        else:
            body['operate'] = 'stop_vm'

        url = '{0}/vm_clone/vm/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVmCloneVmStatus(self, body):
        
        url = '{0}/vm_clone/vm_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机克隆虚机 - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVmCloneVm(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vm_clone/vm/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 历史版本 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleVersion(self, body):
        
        url = '{0}/rule_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 历史版本 - 查看具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleVersionInfo(self, body):
        
        url = '{0}/rule_version/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 回收站 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecycleBin(self, body):
        
        url = '{0}/recycle_bin'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 回收站 - 获取配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRecycleBin(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/recycle_bin//info{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

