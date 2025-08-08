
from info2soft import config
from info2soft import https


class RecoveryRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRecovery(self, body):
        
        url = '{0}/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRecoveryRule(self, body):
        
        url = '{0}/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecoveryRule(self, body):
        
        url = '{0}/recovery_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeRecoveryRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/recovery_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作 开启
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startRecoveryRule(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        
        url = '{0}/recovery_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRecoveryRule(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/recovery_rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 操作 取消
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cancelRecoveryRule(self, body):
        if body is None:
            body = {
                'operate': 'cancel'
            }
        else:
            body['operate'] = 'cancel'

        url = '{0}/recovery_rule/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecoveryRuleStatus(self, body):
        
        url = '{0}/recovery_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 文件恢复 获取目录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDir(self, body):
        
        url = '{0}/recovery_rule/dir'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Oracle 获取恢复点日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTimingRecoveryOracleRcPointInfo(self, body):
        
        url = '{0}/recovery_rule/rc_sbt'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Oracle 获取参数文件列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSbtContrlFile(self, body):
        
        url = '{0}/recovery_rule/sbt_contrlfile'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Oracle 获取DBID
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeSbtDbid(self, body):
        
        url = '{0}/recovery_rule/sbt_dbid'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 验证备份介质 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVerifyBackupMedia(self, body):
        
        url = '{0}/recovery_rule/verify_backup_media'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

