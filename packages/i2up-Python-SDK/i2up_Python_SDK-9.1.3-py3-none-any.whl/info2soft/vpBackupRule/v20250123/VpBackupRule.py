
from info2soft import config
from info2soft import https


class VpBackupRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createVpBackupRule(self, body):
        
        url = '{0}/vp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyVpBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 获取列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpBackupRule(self, body):
        
        url = '{0}/vp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取单个详情
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeVpBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vp/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteVpBackupRule(self, body):
        
        url = '{0}/vp/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateVpBackupRule(self, body):
        
        url = '{0}/vp/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 获取状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVpBackupRuleStatus(self, body):
        
        url = '{0}/vp/backup_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 将虚机加入到规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def taskAddVms(self, body):
        
        url = '{0}/vp/backup_rule/task_add_vms'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

