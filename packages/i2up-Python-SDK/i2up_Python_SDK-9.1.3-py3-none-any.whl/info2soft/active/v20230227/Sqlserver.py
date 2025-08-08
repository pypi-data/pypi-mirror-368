
from info2soft import config
from info2soft import https


class Sqlserver (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * sqlser同步规则-增量失败DML统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesDML(self, body):
        
        url = '{0}/sqlserver/rule/incre_dml_summary'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * sql规则-已同步的对象具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesObjInfo(self, body):
        
        url = '{0}/sqlserver/rule/sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateRule(self, body):
        
        url = '{0}sqlserver/rule/batch_add'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRule(self, body):
        
        url = '{0}/sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRule(self, body):
        
        url = '{0}sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeSqlserverRule(self, body):
        
        url = '{0}/sqlserver/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 状态获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleStatus(self, body):
        
        url = '{0}/sqlserver/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量新建时重名检查
     * 
     * @return list
    '''
    def checkName(self, body):
        
        url = '{0}sqlserver/rule/check_name'.format(config.get_default('default_api_host'))
        
        res = https._post(url, None, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRule(self, body):
        
        url = '{0}sqlserver/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTbCmp(self, body):
        
        url = '{0}/sqlserver/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):
        
        url = '{0}/sqlserver/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeListRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}sqlserver/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/sqlserver/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTbCmp(self, body):
        
        url = '{0}/sqlserver/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则-失败的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesFailObj(self, body):
        
        url = '{0}/sqlserver/rule/fail_obj'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmp(self, body):
        
        url = '{0}/sqlserver/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmpStatus(self, body):
        
        url = '{0}/sqlserver/tb_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 历史结果查看表比较时间结果集
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmpResultTimeList(self, body):
        
        url = '{0}/sqlserver/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTbCmp(self, body):
        
        url = '{0}/sqlserver/tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResuluTimeList(self, body):
        
        url = '{0}/sqlserver/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResult(self, body):
        
        url = '{0}/sqlserver/tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpErrorMsg(self, body):
        
        url = '{0}/sqlserver/tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpCmpResult(self, body):
        
        url = '{0}/sqlserver/tb_cmp/cmp_result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

