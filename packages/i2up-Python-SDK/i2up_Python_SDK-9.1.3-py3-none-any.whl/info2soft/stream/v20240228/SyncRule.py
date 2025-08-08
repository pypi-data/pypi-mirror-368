
from info2soft import config
from info2soft import https


class SyncRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRules(self, body):
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('webapi_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/batch'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchModifySyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/batch'.format(config.get_default('webapi_api_host'))
        
        res = https._put(url, body, self.auth)
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
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopOracleRule(self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartOracleRule (self, body):
        if body is None:
            body = {
                'operate': 'resume'
            }
        else:
            body['operate'] = 'resume'

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
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

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
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

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
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

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
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

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作 继续
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

        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('webapi_api_host'))
        
        res = https._delete(url, body, self.auth)
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
        url = '{0}/vers/v3/sync_rule/{1}'.format(config.get_default('webapi_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesStatus(self, body):
        
        url = '{0}/vers/v3/sync_rule/status'.format(config.get_default('webapi_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-日志（复用旧接口）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):
        
        url = '{0}/active/rule/log'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改维护模式
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchActiveRuleMaintenance(self, body):
        
        url = '{0}/vers/v3/sync_rule/maintenance'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-选择用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleSelectUser(self, body):
        
        url = '{0}/active/rule/select_user'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleTableFix(self, body):
        
        url = '{0}/active/rule/table_fix'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取scn号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleGetScn(self, body):
        
        url = '{0}/active/rule/get_scn'.format(config.get_default('webapi_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-偏移量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listKafkaOffsetInfo(self, body):
        
        url = '{0}/active/rule/kafka_offset'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

