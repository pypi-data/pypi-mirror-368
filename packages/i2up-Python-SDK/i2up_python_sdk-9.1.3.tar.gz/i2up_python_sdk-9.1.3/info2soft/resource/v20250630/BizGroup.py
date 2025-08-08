
from info2soft import config
from info2soft import https


class BizGroup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 1 分组-1 添加
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBizGroup(self, body):
        
        url = '{0}/biz_grp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 分组-2 更新
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBizGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/biz_grp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 1 分组-3 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBizGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/biz_grp/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 1 分组-5 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBizGroup(self, body):
        
        url = '{0}/biz_grp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 1 分组-4 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBizGroup(self, body):
        
        url = '{0}/biz_grp'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2 分组关系-1 更新绑定
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateBizGroupBind(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/biz_grp/{1}/bind'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 2 分组关系-2 获取绑定情况
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listBizGroupBind(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/biz_grp/{1}/bind'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 其他-1 获取 Res 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBizGroupResource(self, body):
        
        url = '{0}/biz_grp/res'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

