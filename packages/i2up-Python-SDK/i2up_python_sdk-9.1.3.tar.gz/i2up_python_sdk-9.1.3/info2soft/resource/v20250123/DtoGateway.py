
from info2soft import config
from info2soft import https


class DtoGateway (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 对象存储网关 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoGateway(self, body):
        
        url = '{0}/vers/v3/dto_gateway'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtoGateway(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dto_gateway/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 获取单条
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDtoGateway(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/dto_gateway/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoGateway(self, body):
        
        url = '{0}/vers/v3/dto_gateway'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoGateway(self, body):
        
        url = '{0}/vers/v3/dto_gateway'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 重置AK/SK
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetDtoGatewayAccessKey(self, body):
        
        url = '{0}/vers/v3/dto_gateway/reset_key'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 获取region绑定列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoGatewayRegions(self, body):
        
        url = '{0}/vers/v3/dto_gateway/region'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 对象存储网关 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getDtoGatewayStatus(self, body):
        
        url = '{0}/vers/v3/dto_gateway/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

