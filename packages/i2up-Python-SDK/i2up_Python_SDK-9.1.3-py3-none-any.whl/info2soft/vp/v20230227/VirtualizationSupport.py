
from info2soft import config
from info2soft import https


class VirtualizationSupport (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * Dashboard - 虚机规则 成功率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVpRuleRate(self, body):
        
        url = '{0}/dashboard/vp_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Dashboard - 虚机 保护率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeVmProtectRate(self, body):
        
        url = '{0}/dashboard/vp_vm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpBackup(self, body):
        
        url = '{0}/vp/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/backup/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机备份 - 获取单个（组）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpBackupGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/backup/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机备份 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpBackup(self, body):
        
        url = '{0}/vp/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 列表（组）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpBackupGroup(self, body):
        
        url = '{0}/vp/backup/group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpBackupStatus(self, body):
        
        url = '{0}/vp/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 操作 启停
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVpBackup(self, body):
        
        url = '{0}/vp/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpBackup(self, body):
        
        url = '{0}/vp/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机备份 - 删除备份点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpBackupPoint(self, body):
        
        url = '{0}/vp/backup/backup_data'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机恢复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpRecovery(self, body):
        
        url = '{0}/vp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机恢复 - 获取单个 组
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpRecoveryGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/recovery/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机恢复 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRecovery(self, body):
        
        url = '{0}/vp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机恢复 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRecoveryStatus(self, body):
        
        url = '{0}/vp/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startVpRecovery(self, body):
        
        url = '{0}/vp/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机恢复 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpRecovery(self, body):
        
        url = '{0}/vp/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpMove(self, body):
        
        url = '{0}/vp/move'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机复制 - 批量创建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateVpRep(self, body):
        
        url = '{0}/vp/rep/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机复制 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpRepGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/rep/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpMove(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/move/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 修改模板
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpMove(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/move/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpMove(self, body):
        
        url = '{0}/vp/move'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpMoveStatus(self, body):
        
        url = '{0}/vp/move/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVpMove(self, body):
        
        url = '{0}/vp/move/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpMove(self, body):
        
        url = '{0}/vp/move'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 虚机迁移/复制 - 获取快照
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRepPointList(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/rep/{1}/point_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 演练规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpDrill(self, body):
        
        url = '{0}/vp/drill'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 演练规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpDrill(self, body):
        
        url = '{0}/vp/drill'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 演练规则 - 获取单个（组）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpDrill(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/drill/group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 演练规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpDrill(self, body):
        
        url = '{0}/vp/drill'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 演练规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpDrillStatus(self, body):
        
        url = '{0}/vp/drill/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 演练规则 - 获取控制台地址
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getConsoleUrl(self, body):
        
        url = '{0}/vp/drill/console_url'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 演练规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopVpDrill(self, body):
        
        url = '{0}/vp/drill/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpFileRecovery(self, body):
        
        url = '{0}/vp/file_recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpFileRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/file_recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpFileRecovery(self, body):
        
        url = '{0}/vp/file_recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpFileRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/file_recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 文件恢复 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def attachVpFileRecovery(self, body):
        
        url = '{0}/vp/file_recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpFileRecoveryStatus(self, body):
        
        url = '{0}/vp/file_recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件恢复 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpFileRecovery(self, body):
        
        url = '{0}/vp/file_recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

