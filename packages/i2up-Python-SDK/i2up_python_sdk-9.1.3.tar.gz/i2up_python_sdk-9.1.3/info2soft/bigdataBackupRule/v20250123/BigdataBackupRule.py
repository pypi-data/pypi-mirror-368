
from info2soft import config
from info2soft import https


class BigdataBackupRule (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 大数据备份 - 列表
     * 
     * @return list
    '''
    def listBigdataBackupRule(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 大数据备份 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigdataBackupRule(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def modifyBigdataBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/bigdata/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigdataBackupRule(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/vers/v3/bigdata/backup_rule/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 大数据备份 - 状态
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupRuleStatus(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def manualStartBigdataBackupRule(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def disableBigdataBackupRule(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableBigdataBackupRule(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 获取备份历史信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupRuleBakHistory(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/bak_history'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 获取Hive表信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupRuleHiveTableInfo(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/hive_table_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大数据备份 - 获取Hive分区信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigdataBackupRuleHivePartitionInfo(self, body):
        
        url = '{0}/vers/v3/bigdata/backup_rule/hive_partition_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

