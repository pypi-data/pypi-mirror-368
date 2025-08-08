
from info2soft import config
from info2soft import https


class BackupMigrate (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 远程校验被迁移控制机状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def decribeCcMoveRemoteStatus(self, body):
        
        url = '{0}/cc_move/check_remote_status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取当前可迁移业务模块关系
     * 
     * @return list
    '''
    def decribeCcMoveModules(self, body):
        
        url = '{0}/cc_move/check_modules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置迁移规则 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createCcMove(self, body):
        
        url = '{0}/cc_move'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 配置迁移规则 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def decribeCcMoveStatus(self, body):
        
        url = '{0}/cc_move/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置迁移规则 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listCcMove(self, body):
        
        url = '{0}/cc_move'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置迁移规则 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteCcMove(self, body):
        
        url = '{0}/cc_move'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 获取单表数据（控制机后端调用）
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def decribeCcMoveTable(self, body):
        
        url = '{0}/cc_move/table'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 配置迁移规则 - 重新迁移
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def makeCcMoveRemigrate(self, body):
        
        url = '{0}/cc_move/remigrate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

