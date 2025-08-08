
from info2soft import config
from info2soft import https


class GeneralInterface (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 版本信息
     * 
     * @return list
    '''
    def describeVersion(self, body):
        
        url = '{0}/version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 新版本信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def latestVersion(self, body):
        
        url = '{0}/check/latest_version'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取版本提交记录
     * 
     * @return list
    '''
    def listVersionHistory(self, body):
        
        url = '{0}/version_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 连接测试
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeConnectTest(self, body):
        
        url = '{0}/node/connect_test'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Dashboard-统一监控平台
     * 
     * @return list
    '''
    def upMonitorOverall(self, body):
        
        url = '{0}/dashboard/up_monitor_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Dashboard-整体状态统计
     * 
     * @return list
    '''
    def overall(self, body):
        
        url = '{0}/dashboard/overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Dashboard-sysadmin
     * 
     * @return list
    '''
    def sysadmin(self, body):
        
        url = '{0}/dashboard/user_summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 总览
     * 
     * @return list
    '''
    def statusOverall(self, body):
        
        url = '{0}/dashboard/status_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 数据集成 总览
     * 
     * @return list
    '''
    def statusStreamOverall(self, body):
        
        url = '{0}/dashboard/stream_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 总览 日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listOverallLogs(self, body):
        
        url = '{0}/dashboard/overall_logs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 概览 - 资源管理
     * 
     * @return list
    '''
    def listOverallResourceSta(self, body):
        
        url = '{0}/dashboard/overall_resource'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 实时数据复制
     * 
     * @return list
    '''
    def listOverallRealTimeCopy(self, body):
        
        url = '{0}/dashboard/overall_real_time_copy'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 应用高可用
     * 
     * @return list
    '''
    def listOverallHa(self, body):
        
        url = '{0}/dashboard/overall_ha'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 副本管理
     * 
     * @return list
    '''
    def listOverallCdm(self, body):
        
        url = '{0}/dashboard/overall_cdm'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 系统迁移
     * 
     * @return list
    '''
    def listOverallFspMv(self, body):
        
        url = '{0}/dashboard/overall_fsp_mv'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 节点/复制规则 兼容6.1
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeRepSummary(self, body):
        
        url = '{0}/dashboard/node_rep_summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 概览 - 虚机概览，获取任务成功率
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpRuleStat(self, body):
        
        url = '{0}/dashboard/vp_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 概览 - 周期性定时数据复制规则概览
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listSchedule(self, body):
        
        url = '{0}/dashboard/schedule_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 概览 - 总览 大数据冷热数据
     * 
     * @return list
    '''
    def getDashboardHotColdData(self, body):
        
        url = '{0}/dashboard/hot_cold_data'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 概览 - 总览V9
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getDashboardStatOverall(self, body):
        
        url = '{0}/dashboard/stat_overall'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 总览 - 板块信息 - 更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateDashboardPlate(self, body):
        
        url = '{0}/dashboard/plate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 总览 - 板块信息 - 获取
     * 
     * @return list
    '''
    def getDashboardPlate(self, body):
        
        url = '{0}/dashboard/plate'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 展示列 - 新建|修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createColumnExt(self, body):
        
        url = '{0}/column_list'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 展示列 - 单个
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeColumnext(self, body):
        
        url = '{0}/column_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 导出规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportRules(self, body):
        
        url = '{0}/export_rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 导入规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importRules(self, body):
        
        url = '{0}/import_rules'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listStatisticsReport(self, body):
        
        url = '{0}/statistics/report'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 签署CSR
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def csrSign(self, body):
        
        url = '{0}/pki/csr_sign'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 证书清单
     * 
     * @return list
    '''
    def listCerts(self, body):
        
        url = '{0}/pki/certs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 下载根证书
     * 
     * @return list
    '''
    def downloadCa(self, body):
        
        url = '{0}/pki/download_ca'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 异步rpc任务列表
     * 
     * @return list
    '''
    def listRpcTask(self, body):
        
        url = '{0}/rpc_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 后台任务列表
     * 
     * @return list
    '''
    def listCronTask(self, body):
        
        url = '{0}/cron_task'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 后台任务删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCronTask(self, body):
        
        url = '{0}/cron_task'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

