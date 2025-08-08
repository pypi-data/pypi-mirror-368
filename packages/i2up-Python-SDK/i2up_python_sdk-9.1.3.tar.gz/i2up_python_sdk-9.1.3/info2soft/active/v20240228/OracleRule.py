from info2soft import config
from info2soft import https


class OracleRule(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 同步规则-数据库预检（已废弃）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleDbCheckMult(self, body):

        url = '{0}/active/rule/db_check_mult'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-已同步的对象具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesObjInfo(self, body):

        url = '{0}/active/rule/sync_obj_info'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-增量失败DML统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesDML(self, body):

        url = '{0}/active/rule/incre_dml_summary'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步|对象比较|对象修复|表比较 - 新建-准备-获取代理状态
     * 
     * @return list
    '''

    def describeSyncRulesProxyStatus(self, body):

        url = '{0}/active/rule/proxy_status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createOracleRule(self, body):

        url = '{0}/active/rule'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchOracleRule(self, body):

        url = '{0}/active/rule/batch'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def modifyOracleRule(self, body):

        url = '{0}/active/rule'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyOracleRuleBatch(self, body):

        url = '{0}/active/rule/batch'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteOracleRule(self, body):

        url = '{0}/active/rule'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则-列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listSyncRules(self, body):

        url = '{0}/active/rule'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/rule/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resumeOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 开始日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def startAnalysisOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'start_analysis'
            }
        else:
            body['operate'] = 'start_analysis'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAnalysisOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 重新日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def resetAnalysisOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_analysis'
            }
        else:
            body['operate'] = 'reset_analysis'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止规则并停止日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopAndStopanalysisOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_and_stopanalysis'
            }
        else:
            body['operate'] = 'stop_and_stopanalysis'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopScheduleOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_schedule'
            }
        else:
            body['operate'] = 'stop_schedule'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 启动调度 暂弃
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def startScheduleOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'start_schedule'
            }
        else:
            body['operate'] = 'start_schedule'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def duplicateOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'duplicate'
            }
        else:
            body['operate'] = 'duplicate'

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listRuleLog(self, body):

        url = '{0}/active/rule/log'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listSyncRulesStatus(self, body):

        url = '{0}/active/rule/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 通用状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listSyncRulesGeneralStatus(self, body):

        url = '{0}/active/rule/general_status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-已同步的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesHasSync(self, body):

        url = '{0}/active/rule/sync_obj'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-失败的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesFailObj(self, body):

        url = '{0}/active/rule/fail_obj'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-装载信息流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesLoadInfo(self, body):

        url = '{0}/active/rule/load_info'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-增量失败dml
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listRuleIncreDml(self, body):

        url = '{0}/active/rule/incre_dml'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-已同步表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listRuleSyncTable(self, body):

        url = '{0}/active/rule/sync_table'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取数据库表字段
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleZStructure(self, body):

        url = '{0}/active/rule/z_structure'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesMrtg(self, body):

        url = '{0}/active/rule/mrtg'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-装载延迟统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listRuleLoadDelayReport(self, body):

        url = '{0}/active/rule/load_delay_report'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-增量失败ddl
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSyncRulesIncreDdl(self, body):

        url = '{0}/active/rule/incre_ddl'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-数据库预检
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleDbCheck(self, body):

        url = '{0}/active/rule/db_check'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取残留规则
     * 
     * @return list
    '''

    def describeRuleGetFalseRule(self, body):

        url = '{0}/active/rule/get_false_rule'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-选择用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleSelectUser(self, body):

        url = '{0}/active/rule/select_user'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleTableFix(self, body):

        url = '{0}/active/rule/table_fix'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取scn号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeRuleGetScn(self, body):

        url = '{0}/active/rule/get_scn'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取接管SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getRevertRpcScn(self, body):

        url = '{0}/active/rule/get_revert_rpc_scn'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-装载统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listRuleLoadReport(self, body):

        url = '{0}/active/rule/load_report'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjCmp(self, body):

        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createObjCmp(self, body):

        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteObjCmp(self, body):

        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeObjCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/obj_cmp/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, None, self.auth)
        return res

    '''
     * 对象比较 - 操作 - 停止
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def cmpStopObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop'
            }
        else:
            body['operate'] = 'cmp_stop'

        url = '{0}/active/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作 - 重启
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def cmpRestartObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/active/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作 - 立即比较
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def cmpImmediateObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_immediate'
            }
        else:
            body['operate'] = 'cmp_immediate'

        url = '{0}/active/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作 - 停止定时
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def cmpStopTimeObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop_time'
            }
        else:
            body['operate'] = 'cmp_stop_time'

        url = '{0}/active/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作 - 继续定时
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def cmpResumeTimeObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_resume_time'
            }
        else:
            body['operate'] = 'cmp_resume_time'

        url = '{0}/active/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjCmpResultTimeList(self, body):

        url = '{0}/active/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeObjCmpResult(self, body):

        url = '{0}/active/obj_cmp/result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取对象比较状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjCmpStatus(self, body):

        url = '{0}/active/obj_cmp/status'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeObjCmpResultTimeList(self, body):

        url = '{0}/active/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjCmpCmpInfo(self, body):

        url = '{0}/active/obj_cmp/cmp_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象修复 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createObjFix(self, body):

        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象修复 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeObjFix(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/obj_fix/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象修复 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteObjFix(self, body):

        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象修复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjFix(self, body):

        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象修复-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartObjFix(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/active/obj_fix/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象修复-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopObjFix(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/active/obj_fix/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象修复 - 修复结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeObjFixResult(self, body):

        url = '{0}/active/obj_fix/result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象修复--获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listObjFixStatus(self, body):

        url = '{0}/active/obj_fix/status'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createTbCmp(self, body):

        url = '{0}/active/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
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
        url = '{0}/active/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteTbCmp(self, body):

        url = '{0}/active/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTbCmp(self, body):

        url = '{0}/active/tb_cmp'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTbCmpStatus(self, body):

        url = '{0}/active/tb_cmp/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop'
            }
        else:
            body['operate'] = 'cmp_stop'

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作 立即比较
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def cmpImmediateTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_immediate'
            }
        else:
            body['operate'] = 'cmp_immediate'

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作 停止定时
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def cmpStopTimeTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop_time'
            }
        else:
            body['operate'] = 'cmp_stop_time'

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作 继续定时
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def cmpResumeTimeTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_resume_time'
            }
        else:
            body['operate'] = 'cmp_resume_time'

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较 - 历史结果（查看表比较时间结果集）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listTbCmpResultTimeList(self, body):

        url = '{0}/active/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpResuluTimeList(self, body):

        url = '{0}/active/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpResult(self, body):

        url = '{0}/active/tb_cmp/result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpErrorMsg(self, body):

        url = '{0}/active/tb_cmp/error_msg'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-表比对的详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpCmpDesc(self, body):

        url = '{0}/active/tb_cmp/cmp_describe'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpCmpResult(self, body):

        url = '{0}/active/tb_cmp/cmp_result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 备端接管-获取网卡列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listBkTakeoveNetworkCard(self, body):

        url = '{0}/active/bk_takeover/bk_network_card'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 备端接管-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createBkTakeover(self, body):

        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管-查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeBkTakeover(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/bk_takeover/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, None, self.auth)
        return res

    '''
     * 备机接管-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteBkTakeover(self, body):

        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备机接管-接管结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeBkTakeoverResult(self, body):

        url = '{0}/active/bk_takeover/result'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopBkTakeover(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/active/bk_takeover/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备机接管-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartBkTakeover(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/active/bk_takeover/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管-获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listBkTakeoverStatus(self, body):

        url = '{0}/active/bk_takeover/status'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备端接管列表
     * 
     * @return list
    '''

    def listBkTakeover(self, body):

        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 反向规则-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createReverse(self, body):

        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 反向规则-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteReverse(self, body):

        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 反向规则-获取单个规则信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeReverse(self, body):

        url = '{0}/active/reverse/rule_single'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 反向规则-获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listReverse(self, body):

        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 反向规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listReverseStatus(self, body):

        url = '{0}/active/reverse/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 反向规则-停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopReverse(self, body):

        url = '{0}/active/reverse/stop'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 反向规则-重启反向任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def restartReverse(self, body):

        url = '{0}/active/reverse/restart'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 反向规则-查看
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeSingleReverse(self, body):

        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))

        res = https._put(url, body, self.auth)
        return res

    '''
     * 日志下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def downloadLog(self, body):

        url = '{0}/active/rule/log_download'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 偏移量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listKafkaOffsetInfo(self, body):

        url = '{0}/active/rule/kafka_offset'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 已同步的对象具体信息(DML解析)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeExtractSyncRulesObjInfo(self, body):

        url = '{0}/active/rule/extract_sync_obj_info'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 已同步的对象具体信息(DML装载)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeLoadSyncRulesObjInfo(self, body):

        url = '{0}/active/rule/load_sync_obj_info'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DML统计 - 表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def increDmlFixAll(self, body):

        url = '{0}/active/rule/table_fix_all'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败统计删除（失败对象）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSyncRulesDML(self, body):

        url = '{0}/active/rule/incre_dml_summary'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getRpcScn(self, body):

        url = '{0}/active/rule/get_rpc_scn'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象比较 - 删除（Oracle菜单）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOracleObjCmp(self, body):

        url = '{0}/active/obj_cmp/obj_cmp_oracle'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较-api 启动比较
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpStart(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/tb_cmp/{1}/start'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量表DML抽取统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIncreDmlExtract(self, body):

        url = '{0}/active/rule/incre_dml_extract'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量表DML装载统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIncreDmlLoad(self, body):

        url = '{0}/active/rule/incre_dml_load'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 解析热点图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listExtractHeatMap(self, body):

        url = '{0}/active/rule/extract_heat_map'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 装载热点图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLoadHeatMap(self, body):

        url = '{0}/active/rule/load_heat_map'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改维护模式
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchActiveRuleMaintenance(self, body):

        url = '{0}/active/rule/maintenance'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 通用操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRuleCommonOperate(self, body):

        url = '{0}/active/rule/common_operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

