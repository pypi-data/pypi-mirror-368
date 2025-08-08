from info2soft import config
from info2soft import https


class ServiceCluster(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 服务集群 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def createServiceCls(self, body):
        url = '{0}/service_cls'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 服务集群 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def modifyServiceCls(self, body, uuid):
        url = '{0}/service_cls/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._put(url, body, self.auth)
        return res

    '''
     * 服务集群 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def deleteServiceCls(self, body):
        url = '{0}/service_cls'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 服务集群 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''

    def describeServiceCls(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/service_cls/{1}'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, None, self.auth)
        return res

    '''
     * 服务集群 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listServiceCls(self, body):
        url = '{0}/service_cls'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务集群 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listServiceClsStatus(self, body):
        url = '{0}/service_cls/status'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务集群 - 集群节点检查 是否可删
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def chkServiceClsNode(self, body):
        url = '{0}/service_cls/cls_node_chk'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务集群 - 配置 编辑
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def configServiceCls(self, body):
        url = '{0}/service_cls/config'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 服务集群 - 配置 获取
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def describeServiceClsConfig(self, body):
        url = '{0}/service_cls/config'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 服务集群 - 获取有效节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''

    def listServiceClsValidNode(self, body):
        url = '{0}/service_cls/valid_node'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

