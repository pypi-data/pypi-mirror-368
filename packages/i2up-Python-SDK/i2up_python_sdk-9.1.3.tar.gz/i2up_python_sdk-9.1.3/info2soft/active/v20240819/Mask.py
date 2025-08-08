
from info2soft import config
from info2soft import https


class Mask (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 敏感类型列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTypes(self, body):
        
        url = '{0}/mask/sens_type'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取总览列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSummaryView(self, body):
        
        url = '{0}/mask/summary/list_view'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改敏感类型
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySensType(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_type/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取单个类型
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptSensType(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_type/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建脱敏算法
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAlgo(self, body):
        
        url = '{0}/mask/algo'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏算法列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAlgos(self, body):
        
        url = '{0}/mask/algo'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个算法
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def descriptAlgo(self, body, id):
        if id is None:
            exit()
        url = '{0}/mask/algo/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 脱敏规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMaskRules(self, body):
        
        url = '{0}/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建脱敏规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMaskRules(self, body):
        
        url = '{0}/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作脱敏规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startMaskRule(self, body):
        
        url = '{0}/mask/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作脱敏规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopMaskRule(self, body):
        
        url = '{0}/mask/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除脱敏规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMaskRule(self, body):
        
        url = '{0}/mask/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取单条脱敏规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeMaskRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取脱敏状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMaskRuleStatus(self, body):
        
        url = '{0}/mask/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个集合
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_db_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 类型列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listMap(self, body):
        
        url = '{0}/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建集合
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createMap(self, body):
        
        url = '{0}/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改集合
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除集合
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteMap(self, body):
        
        url = '{0}/mask/sens_map'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 新建数据库集合
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDbMap(self, body):
        
        url = '{0}/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库集合列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbMap(self, body):
        
        url = '{0}/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除数据库集合
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDbMap(self, body):
        
        url = '{0}/mask/sens_db_map'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 修改数据库集合
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def modifyDbMap(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_db_map/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 新建敏感发现任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createSensCheck(self, body):
        
        url = '{0}/mask/sens_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改敏感发现任务
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifySensCheck(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_check/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除敏感发现任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteSensCheck(self, body):
        
        url = '{0}/mask/sens_check/delete'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取敏感发现列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheck(self, body):
        
        url = '{0}/mask/sens_check'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个任务详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def descriptSensCheck(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_check/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取任务状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckStatus(self, body):
        
        url = '{0}/mask/sens_check/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取结果
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckResult(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/sens_check/result/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 忽略列获取结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSensCheckIgnoreCol(self, body):
        
        url = '{0}/mask/sens_check/ignore_col'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 总览页面
     * 
     * @return list
    '''
    def listSummary(self, body):
        
        url = '{0}/mask/summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 算法测试
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def algoTest(self, body):
        
        url = '{0}/mask/algo/test'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改规则·
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyMaskRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 脱敏规则审批
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createApprove(self, body):
        
        url = '{0}/mask/rule/approve'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏规则 - 导入脱敏文件配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importMaskRuleInfo(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/mask/rule/import_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

