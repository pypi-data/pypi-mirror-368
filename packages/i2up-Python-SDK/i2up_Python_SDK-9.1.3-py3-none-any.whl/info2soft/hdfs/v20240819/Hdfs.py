
from info2soft import config
from info2soft import https


class Hdfs (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 大数据平台 - 总览
     * 
     * @return list
    '''
    def hdfsSummary(self, body):
        
        url = '{0}/hdfs/summary'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * hdfs同步 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHdfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHdfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * hdfs同步 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startHdfs(self, body):
        
        url = '{0}/hdfs/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopHdfs(self, body):
        
        url = '{0}/hdfs/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsStatus(self, body):
        
        url = '{0}/hdfs/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHdfsCompare(self, body):
        
        url = '{0}/hdfs_compare'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHdfsCompare(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs_compare/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsCompare(self, body):
        
        url = '{0}/hdfs_compare'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHdfsCompare(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs_compare/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * hdfs差异比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHdfsCompare(self, body):
        
        url = '{0}/hdfs_compare'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startHdfsCompare(self, body):
        
        url = '{0}/hdfs_compare/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopHdfsCompare(self, body):
        
        url = '{0}/hdfs_compare/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs差异比较 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsCompareStatus(self, body):
        
        url = '{0}/hdfs_compare/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 差异比较 - 获取历史记录列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsCompareHistory(self, body):
        
        url = '{0}/hdfs_compare/list_compare_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 差异比较 - 获取单个历史记录详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHdfsCompareHistory(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs_compare/{1}/compare_history'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 差异比较 - 删除比较结果历史记录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHdfsCompareHistory(self, body):
        
        url = '{0}/hdfs_compare/compare_history'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 差异比较 - 获取比较结果列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsCompareResult(self, body):
        
        url = '{0}/hdfs_compare/list_compare_result'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 差异比较 - 获取比较结果详情列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsCompareResultDetail(self, body):
        
        url = '{0}/hdfs_compare/list_compare_result_detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

