
from info2soft import config
from info2soft import https


class Cluster (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 1准备-1 集群认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authCls(self, body):
        
        url = '{0}/cls/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1准备-2 集群节点验证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def verifyClsNode(self, body):
        
        url = '{0}/cls/node_verify'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 1准备-3 根据集群IP获取节点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def clsNodeInfo(self, body):
        
        url = '{0}/cls/node_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 2编辑/新建-1 新建集群
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCls(self, body):
        
        url = '{0}/cls'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2编辑/新建-2 获取单个集群
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeCls(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cls/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 2编辑/新建-3 修改集群
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyCls(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cls/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 3列表-1 获取集群列表（基本信息）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCls(self, body):
        
        url = '{0}/cls'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3列表-4 集群操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def clsDetail(self, body):
        
        url = '{0}/cls/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 3列表-2 集群状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listClsStatus(self, body):
        
        url = '{0}/cls/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3列表-3 删除集群
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCls(self, body):
        
        url = '{0}/cls'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 列表 - 状态(RAC)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRacStatus(self, body):
        
        url = '{0}/cls/rac_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 切换维护
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def switchMaintenance(self, body):
        
        url = '{0}/cls/maintenance'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取GAUSS集群信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getGaussInfo(self, body):
        
        url = '{0}/cls/gauss_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Gauss HCS获取实例列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGaussHcsInstances(self, body):
        
        url = '{0}/cls/gauss_hcs_instances'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * Gauss HCS 恢复规则获取默认值
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listGaussHcsDefaultInstance(self, body):
        
        url = '{0}/cls/gauss_hcs_default_instance'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

