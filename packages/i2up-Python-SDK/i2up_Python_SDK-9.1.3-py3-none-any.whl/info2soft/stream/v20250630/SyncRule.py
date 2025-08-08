
from info2soft import config
from info2soft import https


class SyncRule (object):
    def __init__(self, auth):
        self.auth = auth
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
     * 同步规则 - 装载信息流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesLoadInfo(self, body):
        
        url = '{0}/vers/v3/sync_rule/load_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
     * 同步规则 - 流量图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesMrtg(self, body):
        
        url = '{0}/vers/v3/sync_rule/mrtg'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
     * 同步规则 - 已同步表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleSyncTable(self, body):
        
        url = '{0}/vers/v3/sync_rule/sync_table'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
     * 同步规则 - 已同步的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesHasSync(self, body):
        
        url = '{0}/vers/v3/sync_rule/sync_obj'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSyncRuleLog(self, body):
        
        url = '{0}/vers/v3/sync_rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 已同步的对象具体信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesObjInfo(self, body):
        
        url = '{0}/vers/v3/sync_rule/sync_obj_info'.format(config.get_default('default_api_host'))
        
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
     * 同步规则 - 同步失败的对象
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesFailObj(self, body):
        
        url = '{0}/vers/v3/sync_rule/fail_obj'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 选择表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleZStructure(self, body):
        
        url = '{0}/vers/v3/sync_rule/z_structure'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DDL
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesIncreDdl(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_ddl'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleTableFix(self, body):
        
        url = '{0}/vers/v3/sync_rule/table_fix'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DML
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRuleIncreDml(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-获取scn号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetScn(self, body):
        
        url = '{0}/vers/v3/sync_rule//get_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 已同步的对象具体信息(DML解析)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeExtractSyncRulesObjInfo(self, body):
        
        url = '{0}/vers/v3/sync_rule/extract_sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetRpcScn(self, body):
        
        url = '{0}/vers/v3/sync_rule/get_rpc_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 已同步的对象具体信息(DML装载)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeLoadSyncRulesObjInfo(self, body):
        
        url = '{0}/vers/v3/sync_rule/load_sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 从底层获取接管SCN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def ruleGetReverseScn(self, body):
        
        url = '{0}/vers/v3/sync_rule/get_revert_rpc_scn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DML统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSyncRulesDML(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml_summary'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-偏移量信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listKafkaOffsetInfo(self, body):
        
        url = '{0}/vers/v3/sync_rule/kafka_offset'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败统计删除（失败对象）副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSyncRulesDML(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml_summary'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 全量状态统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getRuleFullSyncStat(self, body):
        
        url = '{0}/vers/v3/sync_rule/full_sync_stat'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DML统计 - 表修复
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def increDmlFixAll(self, body):
        
        url = '{0}/vers/v3/sync_rule/table_fix_all'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 环境检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncRulePrecheck(self, body):
        
        url = '{0}/vers/v3/sync_rule/pre_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - DB2获取源端时区
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getDbTimezone(self, body):
        
        url = '{0}/vers/v3/sync_rule/timezone'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 数据库预检副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleDbCheck(self, body):
        
        url = '{0}/vers/v3/sync_rule/db_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportSyncRule(self, body):
        
        url = '{0}/vers/v3/sync_rule/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取LSN
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getStreamRuleLsn(self, body):
        
        url = '{0}/vers/v3/sync_rule/lsn'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据集成 - 总览
     * 
     * @return list
    '''
    def statusStreamOverall(self, body):
        
        url = '{0}/vers/v3/sync_rule/stream_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 同步规则 - 增量失败DDL清除所有信息副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteIncreDML(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则-选择用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleSelectUser(self, body):
        
        url = '{0}/vers/v3/sync_rule/select_user'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 总览 - 数据库同步任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryView(self, body):
        
        url = '{0}/vers/v3/sync_rule/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量表DML抽取统计副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIncreDmlExtract(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml_extract'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 增量表DML装载统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listIncreDmlLoad(self, body):
        
        url = '{0}/vers/v3/sync_rule/incre_dml_load'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据安全总览 - 数据库同步任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryMaskView(self, body):
        
        url = '{0}/vers/v3/mask/rule/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 解析热点图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listExtractHeatMap(self, body):
        
        url = '{0}/vers/v3/sync_rule/extract_heat_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 装载热点图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLoadHeatMap(self, body):
        
        url = '{0}/vers/v3/sync_rule/load_heat_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

