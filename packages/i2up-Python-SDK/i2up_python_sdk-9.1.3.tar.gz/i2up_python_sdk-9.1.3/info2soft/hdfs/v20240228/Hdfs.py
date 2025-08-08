
from info2soft import config
from info2soft import https


class Hdfs (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * hdfs同步 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * hdfs - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyHdfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeHdfs(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hdfs/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * hdfs同步 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHdfs(self, body):
        
        url = '{0}/hdfs'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * hdfs同步 - 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHdfsStatus(self, body):
        
        url = '{0}/hdfs/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

