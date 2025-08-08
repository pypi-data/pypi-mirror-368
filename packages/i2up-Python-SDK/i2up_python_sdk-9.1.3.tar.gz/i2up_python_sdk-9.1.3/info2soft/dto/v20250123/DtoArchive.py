
from info2soft import config
from info2soft import https


class DtoArchive (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 归档数据管理 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoArchive(self, body):
        
        url = '{0}/dto/archive'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理 - 导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportDtoArchiveData(self, body):
        
        url = '{0}/dto/archive/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理 - 获取年份
     * 
     * @return list
    '''
    def getDtoArchiveYear(self, body):
        
        url = '{0}/dto/archive/archive_year'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 归档数据管理 - 下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadDtoArchiveData(self, body):
        
        url = '{0}/dto/archive/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理 - 解冻
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restoreDtoArchiveData(self, body):
        
        url = '{0}/dto/archive/restore'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 规则新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoArchiveReportRule(self, body):
        
        url = '{0}/dto/archive/report_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 规则修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtoArchiveReportRule(self, body):
        
        url = '{0}/dto/archive/report_rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 规则查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtoArchiveReportRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/archive/report_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 归档数据管理统计 - 规则删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoArchiveReportRule(self, body):
        
        url = '{0}/dto/archive/report_rule/'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 规则列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoArchiveReportRule(self, body):
        
        url = '{0}/dto/archive/report_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 导出历史
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoArchiveReportHistory(self, body):
        
        url = '{0}/dto/archive/report_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 归档数据管理统计 - 统计报表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoArchiveReportStatistics(self, body):
        
        url = '{0}/dto/archive/report_statistics'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

