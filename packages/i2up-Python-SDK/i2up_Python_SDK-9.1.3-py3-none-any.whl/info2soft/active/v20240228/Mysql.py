
from info2soft import config
from info2soft import https


class Mysql (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * mysql规则管理-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStreamRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStreamRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 重启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 开始解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startParsingStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'start_parsing'
            }
        else:
            body['operate'] = 'start_parsing'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopParsingStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_parsing'
            }
        else:
            body['operate'] = 'stop_parsing'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 重新解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetParsingStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_parsing'
            }
        else:
            body['operate'] = 'reset_parsing'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 开始加载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startLoadStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'start_load'
            }
        else:
            body['operate'] = 'start_load'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 停止加载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopLoadStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_load'
            }
        else:
            body['operate'] = 'stop_load'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 重新加载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetLoadStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_load'
            }
        else:
            body['operate'] = 'reset_load'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 移除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def removeStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'remove'
            }
        else:
            body['operate'] = 'remove'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 停止调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopScheduleStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_schedule'
            }
        else:
            body['operate'] = 'stop_schedule'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 启动调度
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startScheduleStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'start_schedule'
            }
        else:
            body['operate'] = 'start_schedule'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 停止解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'stop_analysis'
            }
        else:
            body['operate'] = 'stop_analysis'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 开始解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'start_analysis'
            }
        else:
            body['operate'] = 'start_analysis'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-操作 重置解析
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetAnalysisStreamRule(self, body):
        if body is None:
            body = {
                'operate': 'reset_analysis'
            }
        else:
            body['operate'] = 'reset_analysis'

        url = '{0}/stream/rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamRules(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql规则管理-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamStatus(self, body):
        
        url = '{0}/stream/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql规则管理-日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamLog(self, body):
        
        url = '{0}/stream/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-同步状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamSyncStatus(self, body):
        
        url = '{0}/stream/rule/sync_status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-历史信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeHistory(self, body):
        
        url = '{0}/stream/rule/history'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql规则管理-资源占用
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeResource(self, body):
        
        url = '{0}/stream/rule/resouce'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        print(res)
        return res

    '''
     * mysql规则管理-修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyStreamRule(self, body):
        
        url = '{0}/stream/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * mysql规则管理-获取单个信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeStreamRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-表比较-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createStreamCmp(self, body):
        
        url = '{0}/stream/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql-表比较-获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeStreamCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-表比较-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteStreamRules(self, body):
        
        url = '{0}/stream/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql-表比较-获取规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamCmps(self, body):
        
        url = '{0}/stream/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-表比较-状态接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStreamCmpStatus(self, body):
        
        url = '{0}/stream/tb_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql-表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpStopStreamCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop'
            }
        else:
            body['operate'] = 'cmp_stop'

        url = '{0}/stream/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql-表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpRestartStreamCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/stream/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql-表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCmpResult(self, body):
        
        url = '{0}/stream/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql-表比较-比较结果的查看
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCmpResult(self, body):
        
        url = '{0}/stream/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResult(self, body):
        
        url = '{0}/stream/tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-表比较-单条错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeCmpErrorMsg(self, body):
        
        url = '{0}/stream/tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 历史结果中的修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listFixResult(self, body):
        
        url = '{0}/stream/result_fix_list'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 比较结果列表的导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportCmpResult(self, body):
        
        url = '{0}/stream/export'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 比较结果列表的修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCmpDiffMap(self, body):
        
        url = '{0}/stream/tb_cmp/diff_map'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBkTakeover(self, body):
        
        url = '{0}/stream/bk_takevoer'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备机接管-查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBkTakeover(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/bk_takeover/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 备机接管-删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBkTakeover(self, body):
        
        url = '{0}/stream/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 备机接管-接管结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTakeoverResult(self, body):
        
        url = '{0}/stream/bk_takeover/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管-获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTakeoverStatus(self, body):
        
        url = '{0}/stream/bk_takeover/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 备机接管列表
     * 
     * @return list
    '''
    def listTakeoverList(self, body):
        
        url = '{0}/stream/bk_takeover'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-对象修复-新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createObjFix(self, body):
        
        url = '{0}/stream/obj_fix'.format(config.get_default('default_api_host'))
        
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
        url = '{0}/stream/obj_fix/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-对象修复 -删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteObjFix(self, body):
        
        url = '{0}/stream/obj_fix'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql-对象修复 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjFix(self, body):
        
        url = '{0}/stream/obj_fix'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql-对象修复 - 操作 重启
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

        url = '{0}/stream/obj_fix/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql-对象修复 - 操作 停止
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

        url = '{0}/stream/obj_fix/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象修复 - 修复结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeObjFixResult(self, body):
        
        url = '{0}/stream/obj_fix/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql对象修复--获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjFixStatus(self, body):
        
        url = '{0}/stream/obj_fix/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql对象比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createObjCmp(self, body):

        url = '{0}/stream/obj_cmp'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql对象比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmp(self, body):
        
        url = '{0}/stream/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql对象比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeObjCmpResultTimeList(self, body):
        
        url = '{0}/stream/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql对象比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeObjCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/stream/obj_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * mysql对象比较-比较结果时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmpResultTimeList(self, body):
        
        url = '{0}/stream/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql对象比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteObjCmp(self, body):
        
        url = '{0}/stream/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * mysql获取对象比较状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmpStatus(self, body):
        
        url = '{0}/stream/obj_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * mysql对象比较-比较结果详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listObjCmpCmpInfo(self, body):
        
        url = '{0}/stream/obj_cmp/cmp_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * mysql对象比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeObjCmpResult(self, body):
        
        url = '{0}/stream/obj_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 备机接管 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateTakeover(self, body):

        url = '{0}/stream/bk_takeover/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

