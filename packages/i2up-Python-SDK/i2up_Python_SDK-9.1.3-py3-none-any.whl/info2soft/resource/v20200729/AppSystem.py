
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
        
        res = https._get(url, body, self.auth)
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
        
        url = '{0}/app_sys/get_app_sys_members'.format(config.get_default('default_api_host'))
        
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
     * 获取工作机状态和上次运行时间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def recoveryStatus(self, body):
        
        url = '{0}/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源概览
     * 
     * @return list
    '''
    def resourceView(self, body):
        
        url = '{0}/dashboard/source'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 资源概览 - 获取资源池列表
     * 
     * @return list
    '''
    def listBackupCenter(self, body):

        url = '{0}/dashboard/list_backup_center'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
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

        res = https._get(url, body, self.auth)
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
        
        res = https._get(url, body, self.auth)
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

