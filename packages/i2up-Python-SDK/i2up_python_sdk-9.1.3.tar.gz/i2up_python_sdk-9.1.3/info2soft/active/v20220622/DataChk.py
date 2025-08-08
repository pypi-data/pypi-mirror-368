from info2soft import config
from info2soft import https


class DataChk(object):
    def __init__(self, auth):
        self.auth = auth

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
     * 表比较-操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def stopTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/datacheck/tb_cmp/operate'.format(config.get_default('default_api_host'))

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
                'operate': 'restart'
            }
        else:
            body['operate'] = 'restart'

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
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeTbCmpCmpResult(self, body):

        url = '{0}/datacheck/tb_cmp/cmp_result'.format(config.get_default('default_api_host'))

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
        url = '{0}/datacheck/tb_cmp//describe{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, body, self.auth)
        return res

