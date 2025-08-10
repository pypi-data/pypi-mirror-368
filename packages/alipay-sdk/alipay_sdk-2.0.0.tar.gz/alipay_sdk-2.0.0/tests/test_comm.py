#!/usr/bin/python3
# @Time    : 2019-09-12
# @Author  : Kevin Kong (kfx2007@163.com)

from Crypto.PublicKey import RSA
from alipay.comm import Comm
from alipay.api import AliPay
import unittest


class TestComm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestComm, cls).setUpClass()
        with open("private.txt", "r") as f:
            private_key = RSA.importKey(f.read())
        with open("public.txt", "r") as f:
            publick_key = RSA.importKey(f.read())
        cls.alipay = AliPay("2016101100664659", private_key,
                            sign_type="rsa2", ali_public_key=publick_key, sandbox=True)
        cls.alipay_rsa = AliPay(
            "2016101100664659", private_key, ali_public_key=publick_key, sandbox=True)

    def test_key_str(self):
        """测试以文本方式导入密钥"""
        key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAqslYYdOaHG1c6jNpyUfPw5bNPwCPN8gczE6ezPRf0Ud9KK9DiZIlafNU12IC+x/eLrmtgVdC339l+2dmSB9jDx1gmmYZv5kNx//E+aeohYv2mPD1ITN72qkZMs3NwggDHYpg+BACfFcYfUBMqdozEkm9Ow7srROdQR3ekRlvvq2dGDqjol/UzwkwiVfgbzQiBwAsw6znyXRfn7iT7+9c1+CfxiOTxlVCMa6z0ZTXDEvfPU2ElcHtYpXYGediHikEIrOnEhNX8pnLINguGsLwu0iN9+vx1h2FfnY8gx3f3yTFpPhapFGGpgx4jQrVi/mxVMZi8pqFrKA+v5ud5mHLBwIDAQABAoIBABWjzX8XwL85XDyQpybJ4pl10ivZdkwrHvsEOzrc/AcYd9Nf4b7ctcDnBCkGUjpfn1dsT3/D/sUy70kboOoij/qqTkNCDKEqU4Sz89FuXPwO8AARB/5c96SNKJQ3X4rmWP61OfQ0kxwOLRwxuYUMEMyQa1nAWlzTz2kgz8Ky5mXShKRkb+jdY+9gJhG1goGGqlfFUmPsKpedW18Umh0u3zSBm6ppY79Y+T1BO+sYG6bYDPZoEdOZwIR/qhA2UK6NyRsNLpIEksNRAeauYM/00E4tw88NvjUwHuLvTwQzNh6jbL5QR6dfBuipmxGvGpjAtqG0KDwi+ncT+bUiD6R9wgECgYEA4NRTSwUPmOQTZquT2hvlQSr5iTqqO0cNbVxaaDrl3XecsDdil2nvimfRrxUMwj9ISypGrgIKHhFkcfm4t0ShS7HWMiExsmiyLUx5/ukv4Fvf8B3cbU9Gkcr3SAj9M5QKWONJsKs7wWCZ2SopikPLxwhjgicnIM8LlVYx1Zyla9cCgYEAwnbsJWYm5jDgaSF6ZksiHpCRbH+u3bfsCJHL4igummanEzHdpsIb9UDokuhOp9LRpGY7XOBPHM/0R4wxmW+G/bezO791eeOPp/NvN6FexU40RSnrmCqm+wF8bbW+MmbsscJEbg2YiVmnx3w3PD33LslXOhCnecP6vdkFAsiVNFECgYEAz11GTaUnU57Y/hM2VS7xbf/TE+0V4YKRMdLCV+wq4u9Vh3ot5vWASCmlTlSd5fM0HI+rjQa4ii8Ec9MduXsFQamOo8HV8nV6ESm+Q4yT6d0TWIZSLke2EPYgyUHxN0dNm9pWtynX/W25uICYu7v4EWT9UqgGAM62IlDTue+26xUCgYEAvYq4ZUOKCrf9I7tz2BzHZs82T3CseoN4Vmn1NbxAoFIJ6xWhm5Z7NbNMfVRcxgsgN4NFvSMNOWIgEVS+S3V/N/FDi6rz0BhTvznxX2G0Q9AT9o4Dik+YbfNm2nBYsDvN3P0jQbmSwd1XQYL7O4aSVVH96SSueGrjDQRoc+waMeECgYBV6L539J4DYhgcypAtooFgIEShHP5kVgRE5I+Sgx5kU5LtEa9dP+6tS3nkEDezWDqCl8L9imKuSEoFwYi6kCwyfbtufs5lTTeWwzwwKQb6pXVs6vWjQNbWFjY0VQLErlQVJA1MSgOBC4/D4FKJtwc2rNWHPcjh6VMXhPmcXogoBw==
-----END RSA PRIVATE KEY-----
        """

        alipay = AliPay("2016101100664659", key,
                        sign_type="rsa2", sandbox=True)

        res = alipay.pay.trade_query("12345")
        self.assertEqual(res["code"], '40004', res)

    def test_key_outheader(self):
        """以无格式方式测试"""

        key = """MIIEpAIBAAKCAQEAqslYYdOaHG1c6jNpyUfPw5bNPwCPN8gczE6ezPRf0Ud9KK9DiZIlafNU12IC+x/eLrmtgVdC339l+2dmSB9jDx1gmmYZv5kNx//E+aeohYv2mPD1ITN72qkZMs3NwggDHYpg+BACfFcYfUBMqdozEkm9Ow7srROdQR3ekRlvvq2dGDqjol/UzwkwiVfgbzQiBwAsw6znyXRfn7iT7+9c1+CfxiOTxlVCMa6z0ZTXDEvfPU2ElcHtYpXYGediHikEIrOnEhNX8pnLINguGsLwu0iN9+vx1h2FfnY8gx3f3yTFpPhapFGGpgx4jQrVi/mxVMZi8pqFrKA+v5ud5mHLBwIDAQABAoIBABWjzX8XwL85XDyQpybJ4pl10ivZdkwrHvsEOzrc/AcYd9Nf4b7ctcDnBCkGUjpfn1dsT3/D/sUy70kboOoij/qqTkNCDKEqU4Sz89FuXPwO8AARB/5c96SNKJQ3X4rmWP61OfQ0kxwOLRwxuYUMEMyQa1nAWlzTz2kgz8Ky5mXShKRkb+jdY+9gJhG1goGGqlfFUmPsKpedW18Umh0u3zSBm6ppY79Y+T1BO+sYG6bYDPZoEdOZwIR/qhA2UK6NyRsNLpIEksNRAeauYM/00E4tw88NvjUwHuLvTwQzNh6jbL5QR6dfBuipmxGvGpjAtqG0KDwi+ncT+bUiD6R9wgECgYEA4NRTSwUPmOQTZquT2hvlQSr5iTqqO0cNbVxaaDrl3XecsDdil2nvimfRrxUMwj9ISypGrgIKHhFkcfm4t0ShS7HWMiExsmiyLUx5/ukv4Fvf8B3cbU9Gkcr3SAj9M5QKWONJsKs7wWCZ2SopikPLxwhjgicnIM8LlVYx1Zyla9cCgYEAwnbsJWYm5jDgaSF6ZksiHpCRbH+u3bfsCJHL4igummanEzHdpsIb9UDokuhOp9LRpGY7XOBPHM/0R4wxmW+G/bezO791eeOPp/NvN6FexU40RSnrmCqm+wF8bbW+MmbsscJEbg2YiVmnx3w3PD33LslXOhCnecP6vdkFAsiVNFECgYEAz11GTaUnU57Y/hM2VS7xbf/TE+0V4YKRMdLCV+wq4u9Vh3ot5vWASCmlTlSd5fM0HI+rjQa4ii8Ec9MduXsFQamOo8HV8nV6ESm+Q4yT6d0TWIZSLke2EPYgyUHxN0dNm9pWtynX/W25uICYu7v4EWT9UqgGAM62IlDTue+26xUCgYEAvYq4ZUOKCrf9I7tz2BzHZs82T3CseoN4Vmn1NbxAoFIJ6xWhm5Z7NbNMfVRcxgsgN4NFvSMNOWIgEVS+S3V/N/FDi6rz0BhTvznxX2G0Q9AT9o4Dik+YbfNm2nBYsDvN3P0jQbmSwd1XQYL7O4aSVVH96SSueGrjDQRoc+waMeECgYBV6L539J4DYhgcypAtooFgIEShHP5kVgRE5I+Sgx5kU5LtEa9dP+6tS3nkEDezWDqCl8L9imKuSEoFwYi6kCwyfbtufs5lTTeWwzwwKQb6pXVs6vWjQNbWFjY0VQLErlQVJA1MSgOBC4/D4FKJtwc2rNWHPcjh6VMXhPmcXogoBw=="""

        with self.assertRaises(ValueError):
            alipay = AliPay("2016101100664659", key,
                            sign_type="rsa2", sandbox=True)

    def test_sign(self):
        """RSA生成待签名字符"""
        self.api = AliPay("2014072300007148", None, sandbox=True)
        data = {
            "method": "alipay.mobile.public.menu.add",
            "charset": 'GBK',
            "sign_type": 'RSA2',
            "timestamp": '2014-07-24 03:07:50',
            "biz_content": '{"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}',
            "version": "1.0"
        }

        a = self.api.comm.get_signstr(data)
        s = 'app_id=2014072300007148&biz_content={"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}&charset=GBK&method=alipay.mobile.public.menu.add&sign_type=RSA2&timestamp=2014-07-24 03:07:50&version=1.0'
        self.assertEqual(a, s)

    def test_sign_cert(self):
        """RSA证书生成待签名字符"""
        self.api = AliPay("2014072300007148", None, sign_type="rsa_cert", app_cert_sn="50fa7bc5dc305a4fbdbe166689ddc827",
                          alipay_root_cert_sn="6bc29aa3b4d406c43483ffea81e08d22", sandbox=True)
        data = {
            "method": "alipay.mobile.public.menu.add",
            "charset": 'GBK',
            "sign_type": 'RSA2',
            "timestamp": '2014-07-24 03:07:50',
            "biz_content": '{"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}',
            "version": "1.0"
        }
        a = self.api.comm.get_signstr(data)
        s = 'alipay_root_cert_sn=6bc29aa3b4d406c43483ffea81e08d22&app_cert_sn=50fa7bc5dc305a4fbdbe166689ddc827&app_id=2014072300007148&biz_content={"button":[{"actionParam":"ZFB_HFCZ","actionType":"out","name":"话费充值"},{"name":"查询","subButton":[{"actionParam":"ZFB_YECX","actionType":"out","name":"余额查询"},{"actionParam":"ZFB_LLCX","actionType":"out","name":"流量查询"},{"actionParam":"ZFB_HFCX","actionType":"out","name":"话费查询"}]},{"actionParam":"http://m.alipay.com","actionType":"link","name":"最新优惠"}]}&charset=GBK&method=alipay.mobile.public.menu.add&sign_type=RSA2&timestamp=2014-07-24 03:07:50&version=1.0'
        self.assertEqual(a, s)

    def test_sign_rsa(self):
        """RSA验证签名"""
        data = {
            "method": "alipay.mobile.public.menu.add",
            "charset": 'GBK',
            "sign_type": 'RSA',
            "timestamp": '2014-07-24 03:07:50',
            "biz_content": '123',
            "version": "1.0"
        }

        s = self.alipay_rsa.comm.get_signstr(data)
        v_s = "b5UyLbGui7uUSK5bNZrxQO+wjI4XySnjpT9ODpPx0L45886RsPSfFWfTjXYzAkuRKADJrRYpkk41TBsUhhp4dLPJwU6H/R90NZgQ8hIxKn1in0+GK3hDEJOaiO+bEPLGSNAC2iiyAoEBz1llNkP6EQBgBi7JaiNaASBXrh0gFpZ7X8dKlTSsx7jeDYULlxKbS3EXaIZnx3Jnv/LDBjXuaWNjUoc7v8bLHF8LNDsOQ5MxuGdijVY/rOAnNocCCxYCuftErxhGtqCfxuhKdkLJc4+T5+5VejwR8wcUZLk1PYkU6sF7qs6+YfjLUyFFakLVCXx+BpzXrNDbQU49L1vXgA=="
        self.assertEqual(self.alipay_rsa.comm.gen(s), v_s)

    def test_sign_rsa2(self):
        """RSA2签名验证"""

        data = {
            "method": "alipay.mobile.public.menu.add",
            "charset": 'GBK',
            "sign_type": 'RSA2',
            "timestamp": '2014-07-24 03:07:50',
            "biz_content": '123',
            "version": "1.0"
        }

        s = self.alipay.comm.get_signstr(data)
        v_s = "N/ZcddFYAgPCkHQE5GcvK0vqaxYJhTsAvP9E54Kd4iYcGWY6eWwS56UOyHFelCI7ONOhmHKz/vRTndBQngXoQYNq+U+/e/9wrS4uT/4VMWpnivegvooaVYnGgrdWBIseE33G41xlEZZLXnaA0KShC9H6n2vIrP9Jgx93g4mU2S+ExJttY4rtgQJoJXKlXV1a8DHMoXY5flLF6hbLOUzonLpCnwbdU7L2DV5pHkNwkP38iACqbbTqDy6SQyoFrOhkmZAk1J6m79oTB1lmekO56c+FjYPZ+hegEWVwYqM1cpB3JYUDVZ+EBTIUewOq3U+f8CreJkkf3OjI32d3mGFWCg=="
        self.assertEqual(self.alipay.comm.gen(s), v_s)

    def test_validate_sign(self):
        """异步回调验签"""
        data = {
            'gmt_create': '2019-11-06 12:52:18',
            'charset': 'utf-8',
            'gmt_payment': '2019-11-06 12:52:28',
            'notify_time': '2019-11-06 12:52:29',
            'subject': 'SO015-1',
            'sign': 'cG6uWeaX+5FXAJu7O02CI6b8V5L5Qamo/lz3LWvBVNCni4A5G1oWezCOVsqCEII/jO9mErQoY5ZXIW7uayRDOmp4nVWjl9kppDCNdi0YJHTdvY3WfoEUwc6XbDplUWWn9U5X00CPnUIlYMbfWaFFmsW/PVzhECBP2V08iBvbi2pscykf5LtyskG6gorJjzkNUE/WoOw+LV3JR30U8IFbfys7m67HDYRMjbdfSIGVDxZUfNMbgQK0/P3DyDQ0PbmdiD8w/e8WHM29cocJ20jnu8j5ZXyngWw09R/VAAW+15IHWJ+26JLA+vV/IM4Hp+v7C/my0Q+fpQPTcg6QEM/d5w==',
            'buyer_id': '2088102179514385',
            'passback_params': 'return_url%3Dhttp%3A%2F%2Fproject.mixoo.cn%3A80%2Fpayment%2Falipay%2Fvalidate%26reference%3DSO015-1%26amount%3D1.0%26currency%3DCNY%26csrf_token%3D24cc66c330aed25a1bcc9ca07dfbf8fa568327d6o1573019530%26notify_url%3Dhttp%3A%2F%2Fproject.mixoo.cn%3A80%2Fpayment%2Falipay%2Fnotify',
            'invoice_amount': '1.00',
            'version': '1.0',
            'notify_id': '2019110600222125229014381000618776',
            'fund_bill_list': '[{"amount":"1.00","fundChannel":"ALIPAYACCOUNT"}]',
            'notify_type': 'trade_status_sync',
            'out_trade_no': 'SO015-1',
            'total_amount': '1.00',
            'trade_status': 'TRADE_SUCCESS',
            'trade_no': '2019110622001414381000117218',
            'auth_app_id': '2016101100664659',
            'receipt_amount': '1.00',
            'point_amount': '0.00',
            'app_id': '2016101100664659',
            'buyer_pay_amount': '1.00',
            'sign_type': 'RSA2',
            'seller_id': '2088102179155775'
        }

        self.assertTrue(self.alipay.comm.validate_sign(data))


if __name__ == "__main__":
    unittest.main()
