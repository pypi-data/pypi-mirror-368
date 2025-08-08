
from info2soft import config
from info2soft import https


class Client (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步修改从类型节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSlaveNode(self, body):
        
        url = '{0}/client/update_slave_node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取所有虚拟平台
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVirtualPlatforms(self, body):
        
        url = '{0}/client/get_virtual_platforms'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取指定虚拟平台上的所有规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getVirtualPlatformRules(self, body):
        
        url = '{0}/client/get_virtual_platform_rules'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 复制/NAS规则，创建比较结果
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCompareResult(self, body):

        url = '{0}/client/create_compare_result'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 接收比较与同步任务执行结果（租户 - 暂未用到）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def collectCompareResult(self, body):

        url = '{0}/client/collect_compare_result'.format(config.get_default('default_api_host'))
        print(url)
        res = https._post(url, body, self.auth)
        return res

    '''
     * 上传比较与同步执行差异详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadCompareDiffDetail(self, body):

        url = '{0}/client/upload_diff_detail'.format(config.get_default('default_api_host'))
        print(url)
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取所有对象存储
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getDtoStorageList(self, body):

        url = '{0}/client/get_dto_storage_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res



