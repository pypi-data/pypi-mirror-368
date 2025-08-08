
from info2soft import config
from info2soft import https


class RecycleBin (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 回收站 - 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRecycleBin(self, body):
        
        url = '{0}/recycle_bin'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 回收站 - 获取配置
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRecycleBin(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/recycle_bin/{1}/info'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

