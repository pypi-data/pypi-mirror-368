
from info2soft import config
from info2soft import https


class ActiveNode (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 未激活节点列表
     * 
     * @return list
    '''
    def listInactiveNodes(self, body):
        
        url = '{0}/active/node/inactive_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 激活
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/active/node/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点列表(搜索)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodes(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNode(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/node/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点调试信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNodeDebugInfo(self, body):
        
        url = '{0}/active/node/debug_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 数据库列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbs(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库健康信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDbHealthInfo(self, body):
        
        url = '{0}/active/db/health_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 测试数据库连接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkDbLink(self, body):
        
        url = '{0}/active/db/db_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbStatus(self, body):
        
        url = '{0}/active/db/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 新建数据库节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDb(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改数据库节点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDb(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/db/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 表空间查询接口
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDbSpace(self, body):
        
        url = '{0}/active/db/space_query'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点升级
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upgradeNode(self, body):
        
        url = '{0}/active/node/upgrade'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 删除数据库
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDb(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 批量导入
     * 
     * @return list
    '''
    def batchCreateDbs(self, body):
        
        url = '{0}/active/db/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取单个数据库节点信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDb(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/active/db/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchMaintenance(self, body):

        url = '{0}/active/node/maintenance'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 重新生成
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebuildActiveNode(self, body):

        url = '{0}/active/node/rebuild'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 刷新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refresgActiveNode(self, body):

        url = '{0}/active/node/refresh'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

