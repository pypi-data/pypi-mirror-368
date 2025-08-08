from info2soft import config
from info2soft import https


class Oceanbase(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 同步规则列表
     * 
     * @return list
    '''

    def listOceanRule(self, body):
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createOceanRule(self, body):
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改规则
     * 
     * @return list
    '''

    def modifyOceanRule(self, body):
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 单条规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeOceanRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ocean/rule/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteOceanRule(self, body):
        url = '{0}/ocean/rule'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 开始解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'start_analysis'
            }
        else:
            body['operate'] = 'start_analysis'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 重置解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'reset'
            }
        else:
            body['operate'] = 'reset'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止并停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAndStopAnalysisOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_and_stopanalysis'
            }
        else:
            body['operate'] = 'stop_and_stopanalysis'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopScheduleOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_schedule'
            }
        else:
            body['operate'] = 'stop_schedule'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 启动调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startScheduleOceanRule(self, body):
        if body is None:
            body = {
                'operate': 'start_schedule'
            }
        else:
            body['operate'] = 'start_schedule'

        url = '{0}/ocean/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listOceanRuleLog(self, body):
        url = '{0}/ocean/rule/log'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

