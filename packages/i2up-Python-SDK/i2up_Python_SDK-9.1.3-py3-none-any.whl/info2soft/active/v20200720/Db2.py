from info2soft import config
from info2soft import https


class Db2(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 同步规则列表
     * 
     * @return list
    '''

    def listDbRule(self, body):

        url = '{0}/db2/rule'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createDbRule(self, body):

        url = '{0}/db2/rule'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改规则
     * 
     * @return list
    '''

    def modifyDbRule(self, body):

        url = '{0}/db2/rule'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 单条规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeDbRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/db2/rule/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteDbRule(self, body):

        url = '{0}/db2/rule'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作 - 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopDbRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resumeDbRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartDbRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 开始分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def startAnalysisDbRule(self, body):
        if body is None:
            body = {
                'operate': 'start_analysis'
            }
        else:
            body['operate'] = 'start_analysis'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 停止分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAnalysisDbRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 重新分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resetAnalysisDbRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_analysis'
            }
        else:
            body['operate'] = 'reset_analysis'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 停止并且停止分析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAndStopAnalysisDbRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_and_stopanalysis'
            }
        else:
            body['operate'] = 'stop_and_stopanalysis'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 停止调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopScheduleDbRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_schedule'
            }
        else:
            body['operate'] = 'stop_schedule'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 - 启动调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def startScheduleDbRule(self, body):
        if body is None:
            body = {
                'operate': 'start_schedule'
            }
        else:
            body['operate'] = 'start_schedule'

        url = '{0}/db2/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listDbRuleLog(self, body):

        url = '{0}/db2/rule/log'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * db2-表比较-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createDb2Cmp(self, body):

        url = '{0}/db2/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * db2表比较-获取
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeDb2Cmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/db2/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * db2-表比较-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteDb2Rules(self, body):

        url = '{0}/db2/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * db2-表比较-获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listDb2Cmps(self, body):

        url = '{0}/db2/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * db2-表比较-状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listDb2CmpStatus(self, body):

        url = '{0}/db2/tb_cmp/status'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * db2-表比较-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def cmpStopDb2Cmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop'
            }
        else:
            body['operate'] = 'cmp_stop'

        url = '{0}/db2/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * db2-表比较-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def cmpRestartDb2Cmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/db2/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * db2-表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteCmpResult(self, body):

        url = '{0}/db2/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * db2-表比较-比较结果的查看
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listCmpResult(self, body):

        url = '{0}/db2/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * db2表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpResult(self, body):

        url = '{0}/db2/tb_cmp/result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * db2-表比较-查看单条
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listDb2ResultFix(self, body):

        url = '{0}/db2/result_fix_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * db2-表比较-单条错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeCmpErrorMsg(self, body):

        url = '{0}/db2/tb_cmp/error_msg'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 比较结果列表的修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listFixResult(self, body):

        url = '{0}/db2/result_fix_list'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 比较结果列表的导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def exportCmpResult(self, body):

        url = '{0}/db2/export'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 历史结果中的修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listCmpDiffMap(self, body):

        url = '{0}/db2/tb_cmp/diff_map'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

