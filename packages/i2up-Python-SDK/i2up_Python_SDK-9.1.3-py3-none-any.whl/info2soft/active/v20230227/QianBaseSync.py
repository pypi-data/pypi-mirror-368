
from info2soft import config
from info2soft import https


class QianBaseSync (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * qianbase同步规则-列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * qianbase规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseStatus(self, body):
        
        url = '{0}/qianbase/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeQianbaseRule(self, body):
        
        url = '{0}/qianbase/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbaseRuleLog(self, body):
        
        url = '{0}/qianbase/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQianbaseRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/qianbase/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createQbTbCmp(self, body):
        
        url = '{0}/qianbase/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQbTbCmpStatus(self, body):
        
        url = '{0}/qianbase/tb_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQbTbCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/qianbase/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteQbTbCmp(self, body):
        
        url = '{0}/qianbase/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * qianbase表比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQbTbCmp(self, body):
        
        url = '{0}/qianbase/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase 历史结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQbTbCmpResultTimeList(self, body):
        
        url = '{0}/qianbase/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopQbTbCmp(self, body):
        
        url = '{0}/qianbase/tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * qianbase表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQbTbCmpResuluTimeList(self, body):
        
        url = '{0}/qianbase/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * qianbase表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQbTbCmpResult(self, body):
        
        url = '{0}/qianbase/tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较-错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQbTbCmpErrorMsg(self, body):
        
        url = '{0}/qianbase/tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase表比较-比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeQbTbCmpCmpResult(self, body):
        
        url = '{0}/qianbase/tb_cmp/cmp_result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

