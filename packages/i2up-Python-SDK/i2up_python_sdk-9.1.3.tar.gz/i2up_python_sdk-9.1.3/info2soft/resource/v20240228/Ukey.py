
from info2soft import config
from info2soft import https


class Ukey (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * Ukey - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createUkey(self, body):
        
        url = '{0}/ukey'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyUkey(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ukey/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * Ukey - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def discribeUkey(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ukey/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Ukey - 列表
     * 
     * @return list
    '''
    def listUkey(self, body):
        
        url = '{0}/ukey'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * Ukey - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteUkey(self, body):
        
        url = '{0}/ukey'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * Ukey - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateUkey(self, body):
        
        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 操作 重置Ukey
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def resetUkey(self, body):
        if body is None:
            body = {
                'operate': 'reset'
            }
        else:
            body['operate'] = 'reset'

        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 操作 克隆
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cloneUkey(self, body):
        if body is None:
            body = {
                'operate': 'clone'
            }
        else:
            body['operate'] = 'clone'

        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 操作 查看密钥
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getPwdUkey(self, body):
        if body is None:
            body = {
                'operate': 'get_pwd'
            }
        else:
            body['operate'] = 'get_pwd'

        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 操作 关联节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def bindNodeUkey(self, body):
        if body is None:
            body = {
                'operate': 'bind_node'
            }
        else:
            body['operate'] = 'bind_node'

        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 操作 解除绑定
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def untieNodeUkey(self, body):
        if body is None:
            body = {
                'operate': 'untie_node'
            }
        else:
            body['operate'] = 'untie_node'

        url = '{0}/ukey/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * Ukey - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUkeyStatus(self, body):
        
        url = '{0}/ukey/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Ukey - 获取关联节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listUkeyNodeList(self, body):
        
        url = '{0}/ukey/node_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Ukey - 扫描
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanUkey(self, body):
        
        url = '{0}/ukey/scan'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Ukey - 口令导出接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportUkeyInfo(self, body):
        
        url = '{0}/ukey/export_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Ukey - 口令导入接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importUkeyInfo(self, body):
        
        url = '{0}/ukey/import_info'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

