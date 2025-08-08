
from info2soft import config
from info2soft import https


class RepRecovery (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 恢复-1 新建任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRepRecovery(self, body):
        
        url = '{0}/rep/recovery'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复-1 获取单个任务
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRepRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 恢复-1 修改任务
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateRepRecovery(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/recovery/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 恢复-2 删除任务
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRepRecovery(self, body):
        
        url = '{0}/rep/recovery'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 恢复-2 获取任务列表（基本信息）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepRecovery(self, body):
        
        url = '{0}/rep/recovery'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复-2 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startRepRecovery(self, body):
        
        url = '{0}/rep/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复-2 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopRepRecovery(self, body):
        
        url = '{0}/rep/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复-2 任务操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def clearFinishRepRecovery(self, body):
        
        url = '{0}/rep/recovery/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复-2 任务状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepRecoveryStatus(self, body):
        
        url = '{0}/rep/recovery/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CDP 恢复-1 获取CDP时间范围
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepRecoveryCdpRange(self, body):
        
        url = '{0}/rep/recovery/cdp_range'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * CDP 恢复-1 获取CDP日志列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRepRecoveryCdpLog(self, body):
        
        url = '{0}/rep/recovery/cdp_log'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 - CDP在线查看任意时间点数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def viewRepRecoveryData(self, body):
        
        url = '{0}/rep/recovery/rc_data_view'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 恢复-状态 在线查看任意时间点数据专用
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRcpRecoveryDataViewStatus(self, body):
        
        url = '{0}/rep/recovery/rc_data_view_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 恢复 - 孤儿文件列表-CDP时间点数据
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCDPRcData(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/rep/recovery/{1}/orphan_list'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

