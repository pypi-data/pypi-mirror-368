#!/usr/bin/python3
# @Time    : 2019-09-12
# @Author  : Kevin Kong (kfx2007@163.com)

from alipay.comm import Comm, AntomCore
from alipay.antom import Authorization, Payment
from alipay.pay import Pay
from alipay.koubei.kb import KouBei
from Crypto.PublicKey import RSA
import os
import csv

SANDBOX_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
URL = "https://openapi.alipay.com/gateway.do"

def import_rsa_key(key):
    if not key or type(key) == RSA.RsaKey:
        return key
    try:
        return RSA.importKey(key)
    except Exception as err:
        raise ValueError("Private import failed, please check it.")


class AliPay(object):

    def __init__(self,clientid, private_key, return_url=None, notify_url=None, public_key=None,
                 sign_type="rsa", app_cert_sn=None, alipay_root_cert_sn=None,
                 location="as",sandbox=False):
        """
        初始化API
        参数：
        clientid: 应用id
        private_key: 商户密钥
        app_cert_sn: 应用公钥证书SN
        alipay_root_cert_sn: 支付宝根证书SN
        sign_type: 签名方式(rsa和rsa2两种)
        公钥证书方式下，应用公钥和支付宝证书SN 必填
        """
        self.appid = clientid
        self.url = SANDBOX_URL if sandbox else URL
        self.app_private_key = import_rsa_key(private_key)
        self.ali_public_key = import_rsa_key(public_key)
        self.sign_type = sign_type.upper()
        self.app_cert_sn = app_cert_sn
        self.alipay_root_cert_sn = alipay_root_cert_sn
        self.return_url = return_url
        self.notify_url = notify_url



    comm = Comm()
    pay = Pay()
    koubei = KouBei()


NAURL = "https://open-na.alipay.com"
ASURL = "https://open-sea.alipay.com"
ERURL = "https://open-eu.alipay.com"

ATOM_URLS = {
    "as": ASURL,
    "na": NAURL,
    "er": ERURL
}

class Antom(object):
    def __init__(self,clientid, private_key, return_url=None, notify_url=None, public_key=None,
                 sign_type="rsa2", app_cert_sn=None, alipay_root_cert_sn=None,
                 location="as",sandbox=False):
        self.client_id = clientid
        self.private_key = private_key
        self.url = ATOM_URLS[location]
    comm = AntomCore()
    auth =  Authorization()
    payment = Payment()

    @classmethod
    def list_payment_methods(self):
        """
        list the payment methods.
        """
        methods = []
        with open(os.path.join(os.path.dirname(__file__), "data/methods.csv")) as f:
            for row in csv.reader(f):
                methods.append((row[0], row[1]))
        return methods