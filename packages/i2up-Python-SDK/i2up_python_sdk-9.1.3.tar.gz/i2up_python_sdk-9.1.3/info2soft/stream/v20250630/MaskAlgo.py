
from info2soft import config
from info2soft import https


class MaskAlgo (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 脱敏算法 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createAlgo(self, body):
        
        url = '{0}/vers/v3/mask/algo'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 脱敏算法 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listAlgos(self, body):
        
        url = '{0}/vers/v3/mask/algo'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 脱敏算法 - 单个
     * 
     * @body['id'] String  必填 id
     * @return list
    '''
    def descriptAlgo(self, body, id):
        if id is None:
            exit()
        url = '{0}/vers/v3/mask/algo/{1}'.format(config.get_default('default_api_host'), id)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 算法测试
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def algoTest(self, body):
        
        url = '{0}/vers/v3/mask/algo/test'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

