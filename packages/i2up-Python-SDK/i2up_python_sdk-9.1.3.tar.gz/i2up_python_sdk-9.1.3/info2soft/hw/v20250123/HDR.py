
from info2soft import config
from info2soft import https


class HDR (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 系统设置 - 更新云平台配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateSetting(self, body):
        
        url = '{0}/sys/settings/'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * VDC管理员 - 保存云账户
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyProfile(self, body):
        
        url = '{0}/user/hcs_info'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * VDC管理员 - 查看当前登录用户信息
     * 
     * @return list
    '''
    def listProfile(self, body):
        
        url = '{0}/user/profile/'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取操作日志用户列表
     * 
     * @return list
    '''
    def getOpLogUsers(self, body):
        
        url = '{0}/user/op_log_user'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

