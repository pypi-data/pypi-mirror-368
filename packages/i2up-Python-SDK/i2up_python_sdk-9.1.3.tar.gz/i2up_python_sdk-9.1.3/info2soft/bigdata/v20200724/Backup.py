
from info2soft import config
from info2soft import https


class Backup (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupStatus(self, body):
        
        url = '{0}/bigdata/backup/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataBackup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/bigdata/backup/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     *  操作 start
     * 
     * @body 参考 API 文档
     * @return 
    '''
    def startBigdataBackup(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  操作 stop
     * 
     * @body 参考 API 文档
     * @return 
    '''
    def stopBigdataBackup(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  操作 start_immediately
     * 
     * @body 参考 API 文档
     * @return 
    '''
    def startImmediatelyBigdataBackup(self, body):
        if body is None:
            body = {
                'operate': 'start_immediately'
            }
        else:
            body['operate'] = 'start_immediately'

        url = '{0}/bigdata/backup/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigdataBackup(self, body):
        
        url = '{0}/bigdata/backup'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res