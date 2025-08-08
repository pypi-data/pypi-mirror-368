
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

    '''
     * 统一许可 - 获取指定许可数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getLicenseData(self, body):
        
        url = '{0}/rest/license/data'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 统一许可 - 获取全部许可数据
     * 
     * @return list
    '''
    def getLicenseItems(self, body):
        
        url = '{0}/rest/license/items'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 统一许可 - 获取许可数据描述
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getLicenseDescribe(self, body):
        
        url = '{0}/rest/license/describe'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 统一许可 - 获取许可文件
     * 
     * @return list
    '''
    def getLicenseFiles(self, body):
        
        url = '{0}/rest/license/files'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 统一许可 - 更新许可文件
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateLicenseFile(self, body):
        
        url = '{0}/rest/license/file'.format(config.get_default('default_api_host'))
        
        res = https._put(url, body, self.auth)
        return res

