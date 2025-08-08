
from info2soft import config
from info2soft import https


class DataChk (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 对象比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatacheckObjCmp(self, body):
        
        url = '{0}/datacheck/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDatacheckObjCmp(self, body):
        
        url = '{0}/datacheck/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDatacheckObjCmp(self, body):
        
        url = '{0}/datacheck/obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDatacheckObjCmp(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/datacheck/obj_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop'
            }
        else:
            body['operate'] = 'cmp_stop'
        
        url = '{0}/datacheck/obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpResumeTimeObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_resume_time'
            }
        else:
            body['operate'] = 'cmp_resume_time'

        url = '{0}/datacheck/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/datacheck/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpImmediateObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_immediate'
            }
        else:
            body['operate'] = 'cmp_immediate'

        url = '{0}/datacheck/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpStopTimeObjCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop_time'
            }
        else:
            body['operate'] = 'cmp_stop_time'

        url = '{0}/datacheck/obj_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果时间列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatacheckObjCmpResultTimeList(self, body):
        
        url = '{0}/datacheck/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDatacheckObjCmpResult(self, body):
        
        url = '{0}/datacheck/obj_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取对象比较状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatacheckObjCmpStatus(self, body):
        
        url = '{0}/datacheck/obj_cmp/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDatacheckObjCmpResultTimeList(self, body):
        
        url = '{0}/datacheck/obj_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象比较-比较结果详细信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDatacheckObjCmpCmpInfo(self, body):
        
        url = '{0}/datacheck/obj_cmp/cmp_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTbCmp(self, body):
        
        url = '{0}/datacheck/tb_cmp'.format(config.get_default('default_api_host'))
        
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
        url = '{0}/datacheck/tb_cmp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTbCmp(self, body):
        
        url = '{0}/datacheck/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmp(self, body):
        
        url = '{0}/datacheck/tb_cmp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较 历史结果（查看表比较时间结果集）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTbCmpResultTimeList(self, body):
        
        url = '{0}/datacheck/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-操作
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
        
        url = '{0}/datacheck/tb_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作
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

        url = '{0}/datacheck/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/datacheck/tb_cmp/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果的删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResuluTimeList(self, body):
        
        url = '{0}/datacheck/tb_cmp/result_time_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 表比较-比较任务结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpResult(self, body):
        
        url = '{0}/datacheck/tb_cmp/result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-错误信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpErrorMsg(self, body):
        
        url = '{0}/datacheck/tb_cmp/error_msg'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-比较结果
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpCmpResult(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/datacheck/tb_cmp/cmp_result/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-表比对的详细信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeTbCmpCmpDesc(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/datacheck/tb_cmp/{1}/describe'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 表比较-启动表比对
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTbCmpStart(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/datacheck/tb_cmp/{1}/start'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

