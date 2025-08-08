
from info2soft import config
from info2soft import https


class ActiveNodeV3 (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 库节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbs(self, body):
        
        url = '{0}/vers/v3/active/db'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 测试连接
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkDbLink(self, body):
        
        url = '{0}/vers/v3/active/db/db_check'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDbStatus(self, body):
        
        url = '{0}/vers/v3/active/db/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDbUnified(self, body):
        
        url = '{0}/vers/v3/active/db'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDb(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/active/db/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 查询表空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeDbSpace(self, body):
        
        url = '{0}/vers/v3/active/db/space_query'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDb(self, body):
        
        url = '{0}/vers/v3/active/db'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 导入
     * 
     * @return list
    '''
    def batchCreateDbs(self, body):
        
        url = '{0}/vers/v3/active/db/batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchDbMaintenance(self, body):
        
        url = '{0}/vers/v3/active/db/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDb(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/active/db/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 数据库节点 - 身份认证信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getActiveDbAuthInfo(self, body):
        
        url = '{0}/vers/v3/active/db/auth_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 批量新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchCreateSqlserverDbs(self, body):
        
        url = '{0}/vers/v3/active/db/db_batch'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 数据库节点 - 获取字符集
     * 
     * @return list
    '''
    def getCharset(self, body):
        
        url = '{0}/vers/v3/active/db/charset'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 机器节点 - 未激活节点
     * 
     * @return list
    '''
    def listInactiveNodes(self, body):
        
        url = '{0}/vers/v3/active/node/inactive_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 机器节点 - 激活（新建）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNode(self, body):
        
        url = '{0}/vers/v3/active/node'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeStatus(self, body):
        
        url = '{0}/vers/v3/active/node/status'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodes(self, body):
        
        url = '{0}/vers/v3/active/node'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 机器节点 - 查看
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNode(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/active/node/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 机器节点 - 状态信息实时流量
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def descriptNodeDebugInfo(self, body):
        
        url = '{0}/vers/v3/active/node/debug_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 机器节点 - 修改
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyNode(self, body):
        
        url = '{0}/vers/v3/active/node'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 机器节点 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteNode(self, body):
        
        url = '{0}/vers/v3/active/node'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 机器节点 - 升级
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def upgradeNode(self, body):
        
        url = '{0}/vers/v3/active/node/upgrade'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 维护模式切换
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchMaintenance(self, body):
        
        url = '{0}/vers/v3/active/node/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 重新生成调试信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebuildActiveNode(self, body):
        
        url = '{0}/vers/v3/active/node/rebuild'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 机器节点 - 刷新调试信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refresgActiveNode(self, body):
        
        url = '{0}/vers/v3/active/node/refresh'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 机器节点 - 重启进程
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartAllProcess(self, body):
        
        url = '{0}/vers/v3/active/node/process_restart'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

