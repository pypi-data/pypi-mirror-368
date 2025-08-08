from info2soft import config
from info2soft import https
from info2soft.common.Rsa import Rsa


class Node(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 0 准备-节点认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authNode(self, body):

        url = '{0}/node/auth'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 0 准备-获取节点安装包列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodePackageList(self, body):

        url = '{0}/node/package_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建节点
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def authNode(self, body):
        url = '{0}/node/auth'.format(config.get_default('default_api_host'))
        rsa = Rsa()
        osPwd = rsa.rsaEncrypt(body['os_pwd'])
        body.update({'os_pwd': osPwd})
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取节点容量
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def checkCapacity(self, body):

        url = '{0}/node/check_capacity'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取节点卷组列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listVg(self, body):

        url = '{0}/node/vg'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点- 扫描集群IP获取节点信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHostInfo(self, body):

        url = '{0}/node/host_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 检查节点在线
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def checkNodeOnline(self, body):

        url = '{0}/node/hello'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 按端口批量搜索节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def batchSearchByPort(self, body):

        url = '{0}/node/hello_port_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点 - 获取绑定云主机信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listNodeBindEcs(self, body):

        url = '{0}/node/ecs_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 新建节点
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def createNode(self, body):

        url = '{0}/node'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改节点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def modifyNode(self, body):

        url = '{0}/node/{1}'.format(config.get_default('default_api_host'), body['node']['node_uuid'])
        rsa = Rsa()
        osPwd = rsa.rsaEncrypt(body['node']['os_pwd'])
        body['node'].update({'os_pwd': osPwd})
        randomStr = https._get(url, None, self.auth)[0]['data']['node']['random_str']
        body['node']['random_str'] = randomStr
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取单个节点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''

    def describeNode(self, body):
        if body is None or 'node_uuid' not in body:
            exit()
        url = '{0}/node/{1}'.format(config.get_default('default_api_host'), body['node_uuid'])

        res = https._get(url, None, self.auth)
        return res

    '''
     * 新建节点 - 批量
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def createBatchNode(self, body):

        url = '{0}/node/batch'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取节点存储信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''

    def describeDeviceInfo(self, body):
        if body is None or 'node_uuid' not in body:
            exit()
        url = '{0}/node/{1}/device_info'.format(config.get_default('default_api_host'), body['node_uuid'])

        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取节点列表
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listNode(self, body):

        url = '{0}/node'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def upgradeNode(self, body):

        url = '{0}/node/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def maintainNode(self, body):

        url = '{0}/node/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点状态
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listNodeStatus(self, body):

        url = '{0}/node/status'.format(config.get_default('default_api_host'))
        res = https._get(url, body, self.auth)
        return res

    '''
     * 删除节点
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def deleteNode(self, body):

        url = '{0}/node'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 3 Dashboard - 获取节点列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def node(self, body):

        url = '{0}/dashboard/node'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 1 单项-添加从类型节点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def addSlaveNode(self, body):

        url = '{0}/node/add_slave_node'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取Oracle DB信息 - 表空间
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeGetOracleInfo(self, body):

        url = '{0}/node/oracle_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取MySQL信息 - 数据库名
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def nodeGetMysqlInfo(self, body):

        url = '{0}/node/mysql_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取数据地址列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def dataIpList(self, body):

        url = '{0}/node/data_ip_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 修改数据地址
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDataIp(self, body):

        url = '{0}/node/data_ip'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 单项 - (Win)节点获取磁盘挂载点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDriverLetter(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/node/{1}/driver_letter'.format(config.get_default('default_api_host'), uuid)

        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取 fc 客户端 hba卡信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHbaInfo(self, body):

        url = '{0}/node/hba_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 解绑云主机检查
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def checkUnbindEcs(self, body):

        url = '{0}/node/check_unbind_ecs'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点 - version
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getNodeVersion(self, body):

        url = '{0}/node/version'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点 - 激活
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def activeNode(self, body):

        url = '{0}/node/active'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 节点 - 待激活列表
     * 
     * @return list
    '''
    def listWaitingActiveNode(self, body):

        url = '{0}/node/inactive_list'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点 - Linux安装脚本下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def downloadNodeInstallScript(self, body):

        url = '{0}/node/install_script'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 节点 - 获取安装包下载链接-URL
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getNodePackageUrl(self, body):

        url = '{0}/node/packge_url'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res





