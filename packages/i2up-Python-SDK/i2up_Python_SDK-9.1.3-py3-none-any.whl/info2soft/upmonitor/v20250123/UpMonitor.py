
from info2soft import config
from info2soft import https


class UpMonitor (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * Dashborad-虚拟化概览
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upMonitorVpRuleStat(self, body):
        
        url = '{0}/up_monitor/vp_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Dashboard-总览（系统概览）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upMonitorOverall(self, body):
        
        url = '{0}/up_monitor/overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控-概览概要
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUpMonitorPlatSummary(self, body):
        
        url = '{0}/up_monitor/plat_summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控 - 事件记录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatistics(self, body):
        
        url = '{0}/up_monitor/statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控 - 事件记录下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadStatistics(self, body):
        
        url = '{0}/up_monitor/statistics/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控 - 规则监控
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUpMonitorRules(self, body):
        
        url = '{0}/up_monitor/rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控-操作日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOpLog(self, body):
        
        url = '{0}/up_monitor/op_log'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控 - 用户信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUser(self, body):
        
        url = '{0}/up_monitor/user'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 平台监控 - 用户导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportUsers(self, body):
        
        url = '{0}/up_monitor/user/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 子平台 - 认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authUpMonitor(self, body):
        
        url = '{0}/up_monitor/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 子平台 - 获取子平台token
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeUpMonitorToken(self, body):
        
        url = '{0}/up_monitor/token'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 子平台 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUpMonitor(self, body):
        
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 子平台 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUpMonitor(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/up_monitor/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 子平台 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUpMonitor(self, body):
        
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 子平台 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeUpMonitor(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/up_monitor/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 子平台 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refreshUpMonitor(self, body):
        
        url = '{0}/up_monitor/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 子平台 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUpMonitorStatus(self, body):
        
        url = '{0}/up_monitor/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 子平台 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteUpMonitor(self, body):
        
        url = '{0}/up_monitor'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

