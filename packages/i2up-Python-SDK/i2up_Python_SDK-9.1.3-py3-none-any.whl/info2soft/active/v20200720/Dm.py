from info2soft import config
from info2soft import https


class Dm(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 同步规则列
     * 
     * @return list
    '''

    def listDmRule(self, body):
        url = '{0}/dm/rule'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createDmRule(self, body):
        url = '{0}/dm/rule'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改规则
     * 
     * @return list
    '''

    def modifyDmRule(self, body):
        url = '{0}/dm/rule'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 单条规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeDmRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dm/rule/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteDmRule(self, body):
        url = '{0}/dm/rule'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作规则 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resumeDmRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopDmRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartDmRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 开始解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def startAnalysisDmRule(self, body):
        if body is None:
            body = {
                'operate': 'start_analysis'
            }
        else:
            body['operate'] = 'start_analysis'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAnalysisDmRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 重置解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resetAnalysisDmRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_analysis'
            }
        else:
            body['operate'] = 'reset_analysis'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作规则 停止并停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAndAnalysisDmRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_and_stopanalysis'
            }
        else:
            body['operate'] = 'stop_and_stopanalysis'

        url = '{0}/dm/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listDmRuleLog(self, body):
        url = '{0}/dm/rule/log'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

