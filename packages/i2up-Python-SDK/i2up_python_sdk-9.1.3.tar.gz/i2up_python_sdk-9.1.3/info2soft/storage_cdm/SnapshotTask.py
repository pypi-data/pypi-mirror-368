
from info2soft import config
from info2soft import https


class SnapshotTask (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSnapshotTask(self, body):
        
        url = '{0}/snapshot_task'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def modifySnapshotTask(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/snapshot_task/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._put(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @return list
    '''
    def listSnapshotTask(self, body):
        
        url = '{0}/snapshot_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSnapshotTask(self, body):
        
        url = '{0}/snapshot_task'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSnapshotTaskStatus(self, body):
        
        url = '{0}/snapshot_task/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 快照任务-获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeSnapshotTask(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/snapshot_task/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startSnapshotTask(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/snapshot_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSnapshotTask(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/snapshot_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 立即执行
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startImmediatelySnapshotTask(self, body):
        if body is None:
            body = {
                'operate': 'start_immediately'
            }
        else:
            body['operate'] = 'start_immediately'

        url = '{0}/snapshot_task/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取任务快照列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listSnapshotList(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/snapshot_task/{1}/snapshot_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除任务快照
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSnapshotList(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/snapshot_task/{1}/snapshot_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

