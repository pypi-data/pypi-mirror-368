
from info2soft import config
from info2soft import https


class CompareResult (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCompareResult(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/compare_result/{1}/list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateCompareResult(self, body):
        
        url = '{0}/compare_result/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCompareResult(self, body):
        
        url = '{0}/compare_result'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 查看配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def viewConfig(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/compare_result/{1}/view_config'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 文件差异详细信息列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDiffDetail(self, body):
        
        url = '{0}/diff_detail'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

