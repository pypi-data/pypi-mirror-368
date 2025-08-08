
from info2soft import config
from info2soft import https


class HBase (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 同步规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createHbaseRule(self, body):
        
        url = '{0}/hbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteHbaseRule(self, body):
        
        url = '{0}/hbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 同步规则 - 获取单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeHbaseRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/hbase/rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 同步规则 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateHbaseRule(self, body):
        
        url = '{0}/hbase/rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 同步规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listHbaseRules(self, body):
        
        url = '{0}/hbase/rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

