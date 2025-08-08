
from info2soft import config
from info2soft import https


class BackupWork (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 定时任务 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBackupWork(self, body):
        
        url = '{0}/backup_work'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 定时任务 - 操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebootBackupWork(self, body):
        if body is None:
            body = {
                'operate': 'reboot'
            }
        else:
            body['operate'] = 'reboot'
        
        url = '{0}/backup_work/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 定时任务 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBackupWork(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/backup_work/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 定时任务 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupWork(self, body):
        
        url = '{0}/backup_work'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 定时任务 - 查看任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBackupWorkResult(self, body):
        
        url = '{0}/backup_work/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 过滤器 - 列表
     * 
     * @return list
    '''
    def listBackupWorkFilter(self, body):
        
        url = '{0}/backup_work_filter'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 过滤器 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBackupWorkFilter(self, body):
        
        url = '{0}/backup_work_filter'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 过滤器 - 详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBackupWorkFilter(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_work_filter/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 过滤器 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBackupWorkFilter(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/backup_work_filter/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 过滤器 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBackupWorkFilter(self, body):
        
        url = '{0}/backup_work_filter'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

