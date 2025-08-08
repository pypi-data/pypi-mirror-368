
from info2soft import config
from info2soft import https


class DtoHost (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 主机 - 认证
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def authDtoHost(self, body):
        
        url = '{0}/dto/host/auth'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 主机 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createDtoHost(self, body):
        
        url = '{0}/dto/host'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 主机 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyDtoHost(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 主机 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeDtoHost(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 主机 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoHost(self, body):
        
        url = '{0}/dto/host'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 主机 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listDtoHostStatus(self, body):
        
        url = '{0}/dto/host/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 主机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteDtoHost(self, body):
        
        url = '{0}/dto/host'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 主机 - 归档时间范围
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listArchiveDate(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/archive_date'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 主机 - 获取恢复时间点
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listRcTimePoint(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/rc_time_point'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 主机 - 归档文件列表
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listArchiveFile(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/archive_file'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 主机 - 底层加载规则
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def listLoadRules(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/load_rules'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 主机 - 查看备份记录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBakRecord(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/backup_record'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 主机 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def operateDtoHost(self, body):
        
        url = '{0}/dto/host/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 主机 - 回源
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def revertFile(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/revert_file'.format(config.get_default('default_api_host'), uuid)
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 主机 - 获取回源记录
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRevertRecord(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/dto/host/{1}/revert_record'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

