
from info2soft import config
from info2soft import https


class CloudEcs (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     *  新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createEcs(self, body):
        
        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listEcs(self, body):
        
        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  列表 - 远程登录
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listVncConsole(self, body):
        
        url = '{0}/cloud/ecs/vnc_console'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  状态
     * 
     * @return list
    '''
    def listEcsStatus(self, body):
        
        url = '{0}/cloud/ecs/status'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 云主机 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteEcs(self, body):

        url = '{0}/cloud/ecs'.format(config.get_default('default_api_host'))

        res = https._delete(url, body, self.auth)
        return res

    '''
     * 云主机 - 操作 启动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def startECS(self, body):
        if body is None:
            body = {
                'operate': 'start'
            }
        else:
            body['operate'] = 'start'

        url = '{0}/cloud/ecs/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 操作 停止
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def stopECS(self, body):
        if body is None:
            body = {
                'operate': 'stop'
            }
        else:
            body['operate'] = 'stop'

        url = '{0}/cloud/ecs/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 云主机 - 获取公网私网IP等信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getTakeoverECSInfo(self, body):

        url = '{0}/cloud/ecs/takeover_ecs_info'.format(config.get_default('default_api_host'))

        res = https._get(url, body, self.auth)
        return res

    '''
     *  云主机 - 节点操作 绑定
     * 
     * @return list
    '''
    def bindNode(self, body):
        if body is None:
            body = {
                'operate': 'bind'
            }
        else:
            body['operate'] = 'bind'
        
        url = '{0}/cloud/ecs/node_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  云主机 - 节点操作 解绑
     * 
     * @return list
    '''
    def untieNode(self, body):
        if body is None:
            body = {
                'operate': 'untie'
            }
        else:
            body['operate'] = 'untie'

        url = '{0}/cloud/ecs/node_operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     *  获取空闲挂载点
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def attachPoint(self, body):
        
        url = '{0}/cloud/ecs/attach_point'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  配置演练
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def configRehearse(self, body):
        
        url = '{0}/cloud/ecs/rehearse_conf'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  演练组 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     *  演练组 - 新建/更新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     *  演练组 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteRehearseGroup(self, body):
        
        url = '{0}/cloud/ecs/rehearse_group'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     *  演练组 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeRehearseGroup(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/cloud/ecs/rehearse_group/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res
