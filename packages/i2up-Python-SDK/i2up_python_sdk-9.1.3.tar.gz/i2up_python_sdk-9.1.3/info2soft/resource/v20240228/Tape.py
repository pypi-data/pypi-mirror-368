
from info2soft import config
from info2soft import https


class Tape (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 磁带库 - 扫描
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def sanTapeLibraries(self, body):
        
        url = '{0}/tape_library/scan'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 获取带库驱动器列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeLibraryDrivers(self, body):
        
        url = '{0}/tape_library/drivers'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTapeLibrary(self, body):
        
        url = '{0}/tape_library'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 列表
     * 
     * @return list
    '''
    def listTapeLibrary(self, body):
        
        url = '{0}/tape_library'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 磁带库 - 单个
     * 
     * @body['uuid'] String  必填 节点uuid
     * @return list
    '''
    def describeTapeLibrary(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape_library/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 磁带库 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def modifyTapeLibrary(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape_library/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 磁带库 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTapeLibrary(self, body):
        
        url = '{0}/tape_library'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 磁带库 - 清点 - 刷新
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refreshTapeLibrarySlot(self, body):
        
        url = '{0}/tape_library/refresh_slot'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 清点 - 扫描插槽(废弃)
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def scanSlot(self, body):
        
        url = '{0}/tape_library/scan_slot'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 出库 - 获取Slot
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBusySlot(self, body):
        
        url = '{0}/tape_library/busy_slot'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 入库 - 扫描I/O插槽
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listBusyIeSlot(self, body):
        
        url = '{0}/tape_library/busy_ie_slot'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 操作 入库-移动磁带到插槽
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def importTapeLibrary(self, body):
        if body is None:
            body = {
                'operate': 'import'
            }
        else:
            body['operate'] = 'import'
        
        url = '{0}/tape_library/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 驱动器管理 - 操作 启用禁用
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableTapeLibraryDrivers(self, body):
        if body is None:
            body = {
                'operate': 'enable'
            }
        else:
            body['operate'] = 'enable'
        
        url = '{0}/tape_library/drivers_operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 磁带库 - 驱动器管理 - 操作 装载卸载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def moveTapeLibraryDrivers(self, body):
        if body is None:
            body = {
                'operate': 'move'
            }
        else:
            body['operate'] = 'move'

        url = '{0}/tape_library/drivers_operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带池列表
     * 
     * @return list
    '''
    def listTapePools(self, body):
        
        url = '{0}/tape_media/tape_pools'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 介质 - 磁带池 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createTapePool(self, body):
        
        url = '{0}/tape_media/tape_pool'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带池 - 修改
     * 
     * @body['uuid'] String  必填 节点uuid
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def updateTapePool(self, body, uuid):
        if uuid is None:
            exit()
        url = '{0}/tape_media/tape_pool/{1}'.format(config.get_default('default_api_host'), uuid)
        
        res = https._put(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带池 - 删除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteTapePool(self, body):
        
        url = '{0}/tape_media/tape_pool'.format(config.get_default('default_api_host'))
        
        res = https._delete(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 冻结/解冻
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def freezeTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'freeze'
            }
        else:
            body['operate'] = 'freeze'
        
        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 浏览
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def browseTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'browse'
            }
        else:
            body['operate'] = 'browse'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 重构
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def rebuildTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'rebuild'
            }
        else:
            body['operate'] = 'rebuild'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 出库
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def exportTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'export'
            }
        else:
            body['operate'] = 'export'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 移动
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def moveTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'move'
            }
        else:
            body['operate'] = 'move'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 更新介质
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refreshTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'refresh'
            }
        else:
            body['operate'] = 'refresh'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 操作 擦除
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def eraseTapeMedia(self, body):
        if body is None:
            body = {
                'operate': 'erase'
            }
        else:
            body['operate'] = 'erase'

        url = '{0}/tape_media/operate'.format(config.get_default('default_api_host'))

        res = https._post(url, body, self.auth)
        return res

    '''
     * 介质 - 磁带 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeMedia(self, body):
        
        url = '{0}/tape_media'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看磁带
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeMediaBkData(self, body):
        
        url = '{0}/tape_media/bkdata'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看磁带 - 磁带数据
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeMediaBkFiles(self, body):
        
        url = '{0}/tape_media/bkfiles'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 查看磁带 - 磁带详情
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeMediaDetails(self, body):
        
        url = '{0}/tape_media/details'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 发现新带库
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def refreshTapeLibrary(self, body):
        
        url = '{0}/tape_library/refresh'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 磁带库 - 机械臂主机列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listTapeLibraryRoboticArm(self, body):
        
        url = '{0}/tape_library/robotic_arm_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 设置驱动/磁带冻结次数
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def setTapeLibraryFreezeNumber(self, body):
        
        url = '{0}/tape_library/freeze_number'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

