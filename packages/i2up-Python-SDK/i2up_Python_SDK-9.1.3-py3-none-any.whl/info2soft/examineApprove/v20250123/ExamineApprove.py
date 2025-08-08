
from info2soft import config
from info2soft import https


class ExamineApprove (object):
    def __init__(self, auth):
        self.auth = auth
    '''
     * 审批 - 新建
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def createExamineApprove(self, body):
        
        url = '{0}/examine_approve'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 列表
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listExamineApprove(self, body):
        
        url = '{0}/examine_approve'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 审批 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def approveExamineApprove(self, body):
        
        url = '{0}/examine_approve/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def enableExamineApprove(self, body):
        
        url = '{0}/examine_approve/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def receiptExamineApprove(self, body):
        
        url = '{0}/examine_approve/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 操作
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def deleteExamineApprove(self, body):
        
        url = '{0}/examine_approve/operate'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 审批人列表
     * 
     * @return list
    '''
    def listExamineApproveApproverList(self, body):
        
        url = '{0}/examine_approve/approver_list'.format(config.get_default('default_api_host'))
        
        res = https._get(url, None, self.auth)
        return res

    '''
     * 审批 - 新建 - 文件上传
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def examineApproveImport(self, body):
        
        url = '{0}/examine_approve/import'.format(config.get_default('default_api_host'))
        
        res = https._post(url, body, self.auth)
        return res

    '''
     * 审批 - 查看文件信息
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def listExamineApproveFileInfo(self, body):
        
        url = '{0}/examine_approve/file_info'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

    '''
     * 审批 - 文件下载
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def examineApproveDownlowdFile(self, body):
        
        url = '{0}/examine_approve/download'.format(config.get_default('default_api_host'))
        
        res = https._get(url, body, self.auth)
        return res

