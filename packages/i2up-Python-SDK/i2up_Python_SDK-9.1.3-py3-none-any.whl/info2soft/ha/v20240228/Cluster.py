
from info2soft import config
from info2soft import https


class Cluster (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 应用高可用 - 集群服务器池 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHaCluster(self, body):
        
        url = '{0}/ha/cls_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHaCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/cls_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 删除主机
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHaClusterHost(self, body):
        
        url = '{0}/ha/cls_pool/host'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHaCluster(self, body):
        
        url = '{0}/ha/cls_pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHaCluster(self, body):
        
        url = '{0}/ha/cls_pool'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 hello
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def registerHaCluster(self, body):
        
        url = '{0}/ha/cls_pool/hello'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHaCluster(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/cls_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 集群服务器池 - 名称查重
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkDupName(self, body):
        
        url = '{0}ha/cls_pool/duplicate_name'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 虚IP查重
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHaClusterIpDuplicate(self, body):
        
        url = '{0}ha/cls_pool/cluster_ip_duplicate'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 UuID
     * 
     * @return list
    '''
    def listHaClusterID(self, body):
        
        url = '{0}/ha/cls_pool/cluster_uuid'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 监控信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHaClusterMonitor(self, body):
        
        url = '{0}/ha/cls_pool/monitor'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 网卡信息
     * 
     * @return list
    '''
    def listNicInfo(self, body):
        
        url = '{0}/ha/netif'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHaClusterStatus(self, body):
        
        url = '{0}/ha/cls_pool/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 标签 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createLabel(self, body):
        
        url = '{0}/ha/service_label'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 标签 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyLabel(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/ha/service_label/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 标签 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteLabel(self, body):
        
        url = '{0}/ha/service_label'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 应用高可用 - 集群服务器池 标签 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listLabel(self, body):
        
        url = '{0}/ha/service_label'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

