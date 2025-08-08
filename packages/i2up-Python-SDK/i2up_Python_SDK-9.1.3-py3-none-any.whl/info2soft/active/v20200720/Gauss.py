
from info2soft import config
from info2soft import https


class Gauss (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 高斯同步规则-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createGaussRule(self, body):
        
        url = '{0}/gauss/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyGaussRule(self, body):
        
        url = '{0}/gauss/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteGaussRule(self, body):
        
        url = '{0}/gauss/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeGaussRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/gauss/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopGaussRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/gauss/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartGaussRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/gauss/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGaussRules(self, body):
        
        url = '{0}/gauss/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGaussStatus(self, body):
        
        url = '{0}/gauss/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeGaussTraffic(self, body):
        
        url = '{0}/gauss/rule/mrtg'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeGuassRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/gauss/rule/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库预检测
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dbCheckGuass(self, body):

        url = '{0}gauss/rule/db_check'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 高斯同步规则-日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGuassRuleLog(self, body):

        url = '{0}gauss/rule/log'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

