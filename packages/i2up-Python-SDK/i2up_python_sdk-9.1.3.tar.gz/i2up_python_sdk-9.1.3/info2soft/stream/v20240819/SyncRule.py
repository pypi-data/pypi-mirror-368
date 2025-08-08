
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
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startAnalysisOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAnalysisOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetAnalysisOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopAndStopanalysisOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def duplicateOracleRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBatchSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 批量修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchModifySyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/batch'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule'.format(config.get_default('default_api_host'))
        
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
        url = '{0}/vers/v3/sync_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesStatus(self, body):
        
        url = '{0}/vers/v3/sync_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 分片信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRulesSliceStatus(self, body):
        
        url = '{0}/vers/v3/sync_rule/slice_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-日志（复用旧接口）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleLog(self, body):
        
        url = '{0}/active/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 修改维护模式
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchSyncRuleMaintenance(self, body):
        
        url = '{0}/vers/v3/sync_rule/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-选择用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleUser(self, body):
        
        url = '{0}/active/rule/select_user'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleTableFix(self, body):
        
        url = '{0}/active/rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取scn号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetScn(self, body):
        
        url = '{0}/active/rule/get_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetRpcScn(self, body):
        
        url = '{0}/active/rule/get_rpc_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取接管SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetReverseScn(self, body):
        
        url = '{0}/active/rule/get_revert_rpc_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则-偏移量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listKafkaOffsetInfo(self, body):
        
        url = '{0}/active/rule/kafka_offset'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

