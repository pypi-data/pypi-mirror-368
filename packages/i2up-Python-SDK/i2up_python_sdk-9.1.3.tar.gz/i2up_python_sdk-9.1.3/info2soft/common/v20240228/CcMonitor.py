
from info2soft import config
from info2soft import https


class CcMonitor (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 主界面
     * 
     * @return list
    '''
    def listCcMonitor(self, body):
        
        url = '{0}/cc_monitor'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 单个节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/cc_monitor/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 后台任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCronTask(self, body):

        url = '{0}/cc/cron_task'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 重置后台任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetCronTask(self, body):

        url = '{0}/cc/cron_task_reset'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 修改后台任务时间间隔
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCronTask(self, body):

        url = '{0}/cc/cron_task_modify'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 控制台资源、状态信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeCcGeneralInfo(self, body):

        url = '{0}/cc_monitor/general_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 控制台-服务操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startCcService(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/cc_monitor/service/operation'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 控制台-服务操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def reloadCcService(self, body):
        if body is None:
            body = {
                'operate': 'reload'
            }
        else:
            body['operate'] = 'reload'

        url = '{0}/cc_monitor/service/operation'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 控制台-服务操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopCcService(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/cc_monitor/service/operation'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 控制台-进程操作 kill 终止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def killCcProcess(self, body):
        if body is None:
            body = {
                'operate': 'kill'
            }
        else:
            body['operate'] = 'kill'

        url = '{0}/cc_monitor/process/operation'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

