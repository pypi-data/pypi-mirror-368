
from info2soft import config
from info2soft import https


class Monitor (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 磁盘信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def listDriversInfo(self, body):
        if body is None or 'uuid' not in body: exit()
        url = '{0}/monitor/drivers_info/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 当前硬件信息
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def listPhyInfo(self, body):
        if body is None or 'uuid' not in body: exit()
        url = '{0}/monitor/phy_info/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取图表展示项
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return array
     '''
    def listChartConfig(self, body):
        if body is None or 'uuid' not in body: exit()
        url = '{0}/monitor/chart_config/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 设置图表展示项
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def setChartConfig(self, body):
        
        url = '{0}/monitor/chart_config/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        del body['uuid']
        res = https._post(url, body, self.auth)
        return res

    '''
     * 图表数据
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict body  参数详见 API 手册
     * @return array
     '''
    def listChartData(self, body):
        
        url = '{0}/monitor/chart_data/{1}'.format(config.get_default('default_api_host'), body['uuid'])
        del body['uuid']
        res = https._get(url, body, self.auth)
        return res

    '''
     * 获取备端系统状态（用于平台监控）
     * 
     * @return list
     '''
    def listBkNodeOverall(self, ):

        url = '{0}/monitor/bk_node_overall'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res

    '''
     * 获取备端系统状态（平台监控）
     * 
     * @return list
    '''
    def listBkNodeOverall(self, body):

        url = '{0}/monitor/bk_node_overall'.format(config.get_default('default_api_host'))

        res = https._get(url, None, self.auth)
        return res

