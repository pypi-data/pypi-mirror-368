
from info2soft import config
from info2soft import https


class BatchTask (object):
    def __init__(self, auth):
        self.auth = auth
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
     * 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startBatchTask(self, body):
        
        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBatchTask(self, body):
        
        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBatchTask(self, body):
        
        url = '{0}/batch_task/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

