
from info2soft import config
from info2soft import https


class DtoLifeManagement (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 生命周期 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoLm(self, body):
        
        url = '{0}/dto/lm'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 生命周期 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtoLm(self, body):
        
        url = '{0}/dto/lm'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 生命周期 - 操作 - 启用禁用删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startDtoLm(self, body):
        if body is None:
            body = {
                'type': 'start'
            }
        else:
            body['type'] = 'start'
        
        url = '{0}/dto/lm/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 生命周期 - 操作 - 启用禁用删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopDtoLm(self, body):
        if body is None:
            body = {
                'type': 'stop'
            }
        else:
            body['type'] = 'stop'

        url = '{0}/dto/lm/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 生命周期 - 操作 - 启用禁用删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoLm(self, body):
        if body is None:
            body = {
                'type': 'delete'
            }
        else:
            body['type'] = 'delete'

        url = '{0}/dto/lm/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

