
from info2soft import config
from info2soft import https


class CfsBackup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * CFS - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCfsBackup(self, body):
        
        url = '{0}/cfs_backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * CFS - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCfsBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cfs_backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * CFS - 获取详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCfsBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cfs_backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * CFS - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsBackup(self, body):
        
        url = '{0}/cfs_backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CFS - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCfsBackup(self, body):
        
        url = '{0}/cfs_backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * CFS - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsBackupStatus(self, body):
        
        url = '{0}/cfs_backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CFS - 获取同步任务状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsBackupSyncStatus(self, body):
        
        url = '{0}/cfs_backup/sync_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取节点等待迁移规则数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getWatingMoveNumber(self, body):
        
        url = '{0}/cfs_backup/waiting_move_number'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CFS - 获取历史规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCfsBackupHistory(self, body):
        
        url = '{0}/cfs_backup/list_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res
    '''
     * CFS - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startCfsBackup(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/cfs_backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res
    '''
     * CFS - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCfsBackup(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/cfs_backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res
    '''
     * CFS - 操作 启动，同步任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startSyncCfsBackup(self, body):
        if body is None:
            body = {
                'operate': 'start_sync'
            }
        else:
            body['operate'] = 'start_sync'

        url = '{0}/cfs_backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res
    '''
     * CFS - 操作 停止，同步任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSyncCfsBackup(self, body):
        if body is None:
            body = {
                'operate': 'stop_sync'
            }
        else:
            body['operate'] = 'stop_sync'

        url = '{0}/cfs_backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res
    '''
     * CFS - 操作 迁移
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def moveCfsBackup(self, body):
        if body is None:
            body = {
                'operate': 'move'
            }
        else:
            body['operate'] = 'move'

        url = '{0}/cfs_backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

