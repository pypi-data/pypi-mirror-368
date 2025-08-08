
from info2soft import config
from info2soft import https


class SyncRules (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 已同步的对象具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesObjInfo(self, body):
        
        url = '{0}/active/rule/sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 增量失败DML统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesDML(self, body):
        
        url = '{0}/active/rule/incre_dml_summary'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  新建-准备-获取代理状态
     * 
     * @return list
    '''
    def describeSyncRulesProxyStatus(self, body):
        
        url = '{0}/active/rule/proxy_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSyncRules(self, body):
        
        url = '{0}/active/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySyncRules(self, body):
        
        url = '{0}/active/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 已同步的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesHasSync(self, body):
        
        url = '{0}/active/rule/sync_obj'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 失败的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesFailObj(self, body):
        
        url = '{0}/active/rule/fail_obj'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 装载信息流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesLoadInfo(self, body):
        
        url = '{0}/active/rule/load_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSyncRules(self, body):
        
        url = '{0}/active/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRules(self, body):
        
        url = '{0}/active/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作同步规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateSyncRules(self, body):
        
        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesStatus(self, body):
        
        url = '{0}/active/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesMrtg(self, body):
        
        url = '{0}/active/rule/mrtg'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 增量失败ddl
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesIncreDdl(self, body):
        
        url = '{0}/active/rule/incre_ddl'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个
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
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmp(self, body):
        
        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createObjCmp(self, body):
        
        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteObjCmp(self, body):
        
        url = '{0}/active/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取单个
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
     * 比较结果时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmpResultTimeList(self, body):
        
        url = '{0}/active/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 比较任务结果
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
     * 比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeObjCmpResultTimeList(self, body):
        
        url = '{0}/active/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 比较结果详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmpCmpInfo(self, body):
        
        url = '{0}/active/obj_cmp/cmp_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createObjFix(self, body):
        
        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取单个
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
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteObjFix(self, body):
        
        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjFix(self, body):
        
        url = '{0}/active/obj_fix'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象修复-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateObjFix(self, body):
        
        url = '{0}/active/obj_fix/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  修复结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeObjFixResult(self, body):
        
        url = '{0}/active/obj_fix/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * -获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjFixStatus(self, body):
        
        url = '{0}/active/obj_fix/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTbCmp(self, body):
        
        url = '{0}/active/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取单个
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
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTbCmp(self, body):
        
        url = '{0}/active/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  列表
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
     *  历史结果（查看表比较时间结果集）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmpResultTimeList(self, body):
        
        url = '{0}/active/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateTbCmp(self, body):
        
        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResuluTimeList(self, body):
        
        url = '{0}/active/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResult(self, body):
        
        url = '{0}/active/tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpErrorMsg(self, body):
        
        url = '{0}/active/tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpCmpResult(self, body):
        
        url = '{0}/active/tb_cmp/cmp_result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBkTakeover(self, body):
        
        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 查看
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
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBkTakeover(self, body):
        
        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 接管结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBkTakeoverResult(self, body):
        
        url = '{0}/active/bk_takeover/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateBkTakeover(self, body):
        
        url = '{0}/active/bk_takeover/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取状态
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
    def listBkTakeover(self, ):
        
        url = '{0}/active/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createReverse(self, body):
        
        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteReverse(self, body):
        
        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取单个规则信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeReverse(self, body):
        
        url = '{0}/active/reverse/rule_single'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReverse(self, body):
        
        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listReverseStatus(self, body):
        
        url = '{0}/active/reverse/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopReverse(self, body):
        
        url = '{0}/active/reverse/stop'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 重启反向任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartReverse(self, body):
        
        url = '{0}/active/reverse/restart'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 查看
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSingleReverse(self, body):
        
        url = '{0}/active/reverse'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 选择用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleSelectUser(self, body):
        
        url = '{0}/active/rule/select_user'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取数据库表字段
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleZStructure(self, body):
        
        url = '{0}/active/rule/z_structure'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):
        
        url = '{0}/active/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleTableFix(self, body):
        
        url = '{0}/active/rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 已同步表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleSyncTable(self, body):
        
        url = '{0}/active/rule/sync_table'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 增量失败dml
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleIncreDml(self, body):
        
        url = '{0}/active/rule/incre_dml'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取残留规则
     * 
     * @return list
    '''
    def describeRuleGetFalseRule(self, body):
        
        url = '{0}/active/rule/get_false_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取scn号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleGetScn(self, body):
        
        url = '{0}/active/rule/get_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 装载统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLoadReport(self, body):
        
        url = '{0}/active/rule/load_report'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 装载延迟统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLoadDelayReport(self, body):
        
        url = '{0}/active/rule/load_delay_report'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库预检
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleDbCheck(self, body):
        
        url = '{0}/active/rule/db_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 开始日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 停止日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 重新日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetAnalysisSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 停止规则并停止日志解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAndStopanalysisSyncRules(self, body):

        url = '{0}/active/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象修复-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartObjFix(self, body):

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

        url = '{0}/active/obj_fix/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTbCmp(self, body):

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

        url = '{0}/active/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 备机接管-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopBkTakeover(self, body):

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

        url = '{0}/active/bk_takeover/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
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

