
from info2soft import config
from info2soft import https


class OracleRule (object):
    def __init__(self, auth):
        self.auth = auth
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
     * 同步规则-数据库预检（支持单个或者多个）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRuleDbCheckMult(self, body):
        
        url = '{0}/active/rule/db_check_single'.format(config.get_default('default_api_host'))
        
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
        url = '{0}/active/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resumeOracleRule(self, body):
        
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
     * 同步规则-已同步的对象具体信息(DML解析)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeExtractSyncRulesObjInfo(self, body):
        
        url = '{0}/active/rule/extract_sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则-已同步的对象具体信息(DML解析)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeLoadSyncRulesObjInfo(self, body):
        
        url = '{0}/active/rule/load_sync_obj_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
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
        
        res = https._get(url, None, self.auth)
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
     * 同步规则-日志下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadLog(self, body):
        
        url = '{0}/active/rule/log_download'.format(config.get_default('default_api_host'))
        
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

