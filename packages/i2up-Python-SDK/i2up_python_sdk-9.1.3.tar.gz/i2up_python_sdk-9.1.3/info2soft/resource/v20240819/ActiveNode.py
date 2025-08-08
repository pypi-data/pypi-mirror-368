
from info2soft import config
from info2soft import https


class ActiveNode (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 未激活机器节点列表
     * 
     * @return list
    '''
    def listInactiveNodes(self, body):
        
        url = '{0}/active/node/inactive_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 激活机器节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/active/node/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点列表(搜索)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodes(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 机器节点详细信息
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
     * 状态信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNodeDebugInfo(self, body):
        
        url = '{0}/active/node/debug_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改机器节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 删除机器节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNode(self, body):
        
        url = '{0}/active/node'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 机器节点升级
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upgradeNode(self, body):
        
        url = '{0}/active/node/upgrade'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点升级副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def renewActiveNode(self, body):
        
        url = '{0}/active/node/renew'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点-维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchMaintenance(self, body):
        
        url = '{0}/active/node/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取字符集
     * 
     * @return list
    '''
    def getCharset(self, body):
        
        url = '{0}/active/db/charset'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 库节点 - 维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchDbMaintenance(self, body):
        
        url = '{0}/active/db/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 库节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbs(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 测试数据库连接（7.1.75 ）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkDbLink(self, body):
        
        url = '{0}/active/db/db_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 库节点状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbStatus(self, body):
        
        url = '{0}/active/db/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 库节点-新建 （格式统一7.1.75 ）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDbUnified(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 库节点 - 修改
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
     * 删除库节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDb(self, body):
        
        url = '{0}/active/db'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 库节点 - 批量导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateDbs(self, body):
        
        url = '{0}/active/db/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 批量导入
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateActiveNodes(self, body):
        
        url = '{0}/active/node/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 单个库节点信息
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

    '''
     * 机器节点 - 重启进程
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartAllProcess(self, body):
        
        url = '{0}/active/node/process_restart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 库节点 - 身份认证信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getActiveDbAuthInfo(self, body):
        
        url = '{0}/active/db/auth_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 批量新建（sqlserver）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateSqlserverDbs(self, body):
        
        url = '{0}/active/db/db_batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

