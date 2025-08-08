
from info2soft import config
from info2soft import https


class ObjCmp (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 对象比较 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDatacheckObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDatacheckObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def restartObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpStopTimeObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpResumeTimeObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def cmpImmediateObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 对象比较 - 导出
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportSyncObjCmp(self, body):
        
        url = '{0}/vers/v3/sync_obj_cmp/export'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

