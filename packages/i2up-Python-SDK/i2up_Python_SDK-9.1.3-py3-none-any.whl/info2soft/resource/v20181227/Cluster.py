from info2soft import config
from info2soft import https
from info2soft.common.Rsa import Rsa


class Cluster(object):
    def __init__(self, auth):
        self.auth = auth

    '''
     * 1 集群认证
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def authCls(self, body):
        url = '{0}/cls/auth'.format(config.get_default('default_api_host'))
        rsa = Rsa()
        osPwd = rsa.rsaEncrypt(body['os_pwd'])
        body.update({'os_pwd': osPwd})
        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 集群节点验证
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def verifyClsNode(self, body):
        url = '{0}/cls/node_verify'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 1 新建集群
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def createCls(self, body):
        url = '{0}/cls'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 2 获取单个集群
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''

    def describeCls(self, body):
        if body is None or 'node_uuid' not in body['cls']:
            exit()
        url = '{0}/cls/{1}'.format(config.get_default('default_api_host'), body['cls']['node_uuid'])

        res = https._get(url, None, self.auth)
        return res

    '''
     * 3 修改集群
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def modifyCls(self, body):
        url = '{0}/cls/{1}'.format(config.get_default('default_api_host'), body['cls']['node_uuid'])
        del body['cls']['node_uuid']
        cls = https._get(url, None, self.auth)[0]
        if 'cls' in cls['data']:
            randomStr = https._get(url, None, self.auth)[0]['data']['cls']['random_str']
            body['cls']['random_str'] = randomStr
            res = https._put(url, body, self.auth)
        else:
            res = [cls]
        return res

    '''
     * 1 获取集群列表（基本信息）
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listCls(self, body):
        url = '{0}/cls'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     * 2 集群状态
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def listClsStatus(self, body):
        url = '{0}/cls/status'.format(config.get_default('default_api_host'))
        res = https._get(url, body, self.auth)
        return res

    '''
     * 3 删除集群
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def deleteCls(self, body):
        url = '{0}/cls'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 4 集群操作
     * 
     * @param dict body  参数详见 API 手册
     * @return array
     '''

    def clsDetail(self, body):
        url = '{0}/cls/operate'.format(config.get_default('default_api_host'))

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



