
from info2soft import config
from info2soft import https


class DedupePool (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 重删池 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDedupePool(self, body):
        
        url = '{0}/dedupe_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 重删池 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDedupePool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dedupe_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 重删池 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDedupePool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dedupe_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 重删池 - 列表
     * 
     * @return list
    '''
    def dedupePoolList(self, ):
        
        url = '{0}/dedupe_pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 重删池 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDedupePool(self, body):
        
        url = '{0}/dedupe_pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 重删池 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDedupePoolStatus(self, body):
        
        url = '{0}/dedupe_pool/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 重删池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startDedupePool(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'
        
        url = '{0}/dedupe_pool/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 重删池 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopDedupePool(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/dedupe_pool/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

