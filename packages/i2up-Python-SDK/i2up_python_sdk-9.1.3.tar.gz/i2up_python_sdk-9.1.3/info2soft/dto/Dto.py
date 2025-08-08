
from info2soft import config
from info2soft import https


class Dto (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoRule(self, body):
        
        url = '{0}/dto/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtoRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 规则 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtoRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoRule(self, body):
        
        url = '{0}/dto/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoRuleStatus(self, body):
        
        url = '{0}/dto/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoRule(self, body):
        
        url = '{0}/dto/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 规则 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startDtoRule(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        
        url = '{0}/dto/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopDtoRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/dto/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeDtoRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/dto/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则 - 操作 失败重传
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartDtoRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/dto/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 规则 - 文件列表（比较 不同/丢失/失败/孤儿）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoRuleFile(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/rule/{1}/file'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 规则 - 文件列表 删除孤儿（比较）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def deleteDtoRuleFile(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/rule/{1}/file'.format(config.get_default('default_api_host'), uuid)
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 规则 - 比较结果（比较）
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listDtoRuleCmpResult(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/rule/{1}/cmp_result'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 规则 - 获取源端对应路径列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoRuleSourcePath(self, body):

        url = '{0}/dto/rule/source_path_list'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

