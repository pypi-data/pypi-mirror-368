
from info2soft import config
from info2soft import https


class QianBasexTP (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * qianbasexTP同步规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * qianbase规则-状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * qianbase日志
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listQianbasex(self, body):
        
        url = '{0}/qianbasextp/rule/log'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

