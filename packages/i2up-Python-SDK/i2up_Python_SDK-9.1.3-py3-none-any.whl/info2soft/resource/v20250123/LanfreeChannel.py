
from info2soft import config
from info2soft import https


class LanfreeChannel (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * LANFREE通道 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createLanfreeChannel(self, body):
        
        url = '{0}/lanfree_channel'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * LANFREE通道 - 列表
     * 
     * @return list
    '''
    def listLanfreeChannel(self, body):
        
        url = '{0}/lanfree_channel'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * LANFREE通道 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeLanfreeChannel(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lanfree_channel//{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * LANFREE通道 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyLanfreeChannel(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/lanfree_channel//{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * LANFREE通道 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteLanfreeChannel(self, body):
        
        url = '{0}/lanfree_channel'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * LANFREE通道 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLanfreeChannelStatus(self, body):
        
        url = '{0}/lanfree_channel/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 根据客户端、备端获取lanfree列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLanfreeChannelByWkBk(self, body):
        
        url = '{0}/lanfree_channel/list_by_wk_bk'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * LANFREE通道 - 查看通道
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLanfreeChannelInfo(self, body):
        
        url = '{0}/lanfree_channel/info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

