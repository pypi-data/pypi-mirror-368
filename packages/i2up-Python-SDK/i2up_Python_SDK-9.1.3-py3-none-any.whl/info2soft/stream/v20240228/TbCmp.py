
from info2soft import config
from info2soft import https


class TbCmp (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 表比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTbCmp(self, body):
        
        url = '{0}/vers/v3/sync_tb_cmp'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'
        
        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('webapi_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartTbCmp(self, body):
        if body is None:
            body = {
                'operate': 'cmp_restart'
            }
        else:
            body['operate'] = 'cmp_restart'

        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpStopTime(self, body):
        if body is None:
            body = {
                'operate': 'cmp_stop_time'
            }
        else:
            body['operate'] = 'cmp_stop_time'

        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 表比较-操作副本
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpResumeTime(self, body):
        if body is None:
            body = {
                'operate': 'cmp_resume_time'
            }
        else:
            body['operate'] = 'cmp_resume_time'

        url = '{0}/vers/v3/sync_tb_cmp/operate'.format(config.get_default('webapi_api_host'))

        res = https._post(url, body, self.auth)
        return res

