
from info2soft import config
from info2soft import https


class BigScreen (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 大屏展示 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createBigScreen(self, body):
        
        url = '{0}/big_screen'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyBigScreen(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/big_screen/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeBigScreen(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/big_screen/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigScreen(self, body):
        
        url = '{0}/big_screen'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigScreen(self, body):
        
        url = '{0}/big_screen'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 大屏展示 - logo上传
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def uploadBigScreenLogo(self, body):
        
        url = '{0}/big_screen/logo'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大屏展示 - logo删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteBigScreenLogo(self, body):
        
        url = '{0}/big_screen/logo'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 大屏展示-logo列表
     * 
     * @return list
    '''
    def listBigScreenLogo(self, body):
        
        url = '{0}/big_screen/logo_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 更新配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def configBigScreen(self, body):
        
        url = '{0}/big_screen/config'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 获取配置
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBigScreenConfig(self, body):
        
        url = '{0}/big_screen/config'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 清零
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def clearBigScreenStatData(self, body):
        
        url = '{0}/big_screen/clear_data'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 大屏展示 - 获取规则
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigScreenStatRules(self, body):
        
        url = '{0}/big_screen/rules'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示-统计数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def describeBigScreenStat(self, body):
        
        url = '{0}/big_screen/stat'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 大屏展示-拓扑图
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBigScreenGraph(self, body):
        
        url = '{0}/big_screen/graph'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

