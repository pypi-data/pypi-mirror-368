
from info2soft import config
from info2soft import https


class DistributorSystem (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取配置
     * 
     * @return list
    '''
    def listSysSetting(self, ):
        
        url = '{0}/sys/settings'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     *  更新配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSetting(self, body):
        
        url = '{0}/sys/settings'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  命令列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def queueList(self, body):
        
        url = '{0}/distribution/sys/queue_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  命令列表 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def queueDelete(self, body):
        
        url = '{0}/distribution/sys/queue_list'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  一键升级 - 获取版本
     * 
     * @return list
    '''
    def upgradeVersion(self, ):
        
        url = '{0}/distribution/sys/upgrade_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     *  一键升级
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def update(self, body):
        
        url = '{0}/distribution/sys/upgrade'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  告警统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def alarmStat(self, body):
        
        url = '{0}/distribution/sys/alarm_stat'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  告警日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def alarmLog(self, body):
        
        url = '{0}/distribution/sys/alarm_log'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateAlarmLog(self, body):
        
        url = '{0}/distribution/sys/alarm_log_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新增用户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改用户信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUser(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/user/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 用户列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUser(self, body):
        
        url = '{0}/user'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 用户统计
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def statUser(self, body):
        
        url = '{0}/user/stat'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步网关
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncGateway(self, body):
        
        url = '{0}/distribution/sys/sync_gateway'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步账号
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def syncAccount(self, body):
        
        url = '{0}/distribution/sys/sync_account'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取发送文件信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def sendFiles(self, body):
        
        url = '{0}/distribution/sys/send_files'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

