
from info2soft import config
from info2soft import https


class ReCyle (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecycle(self, body):
        
        url = '{0}/recycle'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除记录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRecycle(self, body):
        
        url = '{0}/recycle'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecycleStatus(self, body):
        
        url = '{0}/recycle/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 清理数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cleanRecycle(self, body):

        url = '{0}/recycle/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

