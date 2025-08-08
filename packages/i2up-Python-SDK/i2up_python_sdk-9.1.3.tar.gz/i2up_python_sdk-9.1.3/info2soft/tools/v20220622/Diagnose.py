
from info2soft import config
from info2soft import https


class Diagnose (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  新建
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def createDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def deleteDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  获取列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listDiagnose(self, body):
        
        url = '{0}/diagnose'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  下载结果
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def downloadDiagnoseResult(self, body):
        
        url = '{0}/diagnose/download_res'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

