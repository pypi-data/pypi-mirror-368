from OpenSSL import crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
import base64
from info2soft import config
from info2soft import https


class Rsa(object):
    def __init__(self):
        self

    '''
     * 获取公钥
     * 
     * @param dict $body  参数详见 API 手册
     * @return list
    '''
    def getPublicSettings(self):

        url = '{0}/sys/public_settings'.format(config.get_default('default_api_host'))

        res = https._get(url, None)
        return res

    def getPublicKey(self, cer_file_path):
        """
        从证书中提取公钥
        :param cer_file_path: 证书存放路径
        :return: 公钥
        """
        cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(cer_file_path, 'rb').read())
        res = crypto.dump_publickey(crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")
        return res.strip()

    # rsa加密
    def rsaEncrypt(self, pwd):
        pemFilePath = os.path.split(os.path.realpath(__file__))[0] + '/public_key.pem'
        # 首先从控制机获取公钥，拿不到用本地的
        pubSettings = self.getPublicSettings()
        if pubSettings[0]['data']['pubKey'] is not None:
            pubkey = pubSettings[0]['data']['pubKey']
        else:
            pubkey = self.getPublicKey(pemFilePath)
        rsaPubkey = RSA.importKey(pubkey)
        cipherPub = PKCS1_OAEP.new(rsaPubkey)
        code = base64.b64encode(cipherPub.encrypt(pwd.encode(encoding="utf-8"))).decode('utf-8')
        return code
