#!/usr/bin/python3
# @Time    : 2019-10-31
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from Crypto.PublicKey import RSA
from alipay.api import AliPay
from autils import string
from autils.string import String
import time


class TestPay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPay, cls).setUpClass()
        with open("private.txt", "r") as f:
            private_key = RSA.importKey(f.read())
        cls.alipay = AliPay("2016101100664659", private_key,
                            sign_type="rsa2", sandbox=True)
        cls.buyer_id = "2088102179514385"
        cls.order_no = String.generate_digits(24)
        print(f"测试订单：{cls.order_no}")

    def test_trade_create(self):
        """测试统一下单"""
        # 测试不存在的用户
        res = self.alipay.pay.trade_create(
            self.order_no, 1.01, "测试统一下单", buyer_id="208810217951438X")
        self.assertEqual(res["code"], "40004")

        res = self.alipay.pay.trade_create(
            self.order_no, 2.00, "测试统一下单", buyer_id=self.buyer_id)
        self.assertEqual(res['code'], '10000')

    def test_trade_pay(self):
        """测试扫码付款"""
        # 收款码错误
        res = self.alipay.pay.trade_pay(
            String.generate_digits(24), "bar_code", "28091756689709104X", "测试中文支付", total_amount=2)
        self.assertEqual(res["code"], '40004')

    def test_trade_close(self):
        """测试统一收单关闭接口"""
        # 测试关闭订单
        # 支付宝沙箱环境总是返回20000
        res = self.alipay.pay.trade_close(
            out_trade_no="190507823711243775320439")
        self.assertIn(res["code"], ['10000', '20000'], msg=res)

    def test_trade_query(self):
        """统一收单线下交易查询"""
        res = self.alipay.pay.trade_query(self.order_no)
        self.assertEqual(res["code"], "10000", msg=res)

    def test_trade_refund(self):
        """测试统一收单交易退款接口"""
        # 收款后状态才能退款，因此接口总是返回40004
        res = self.alipay.pay.trade_refund(1, out_trade_no=self.order_no)
        self.assertEqual(res["code"], "40004", res)

    def test_trade_refund_query(self):
        """测试统一收单退款查询"""
        res = self.alipay.pay.trade_fastpay_refund_query(
            self.order_no, out_trade_no=self.order_no)
        self.assertEqual(res["code"], "10000", msg=res)

    def test_precreate(self):
        """统一收单线下交易预创建"""
        res = self.alipay.pay.trade_precreate(
            String.generate_digits(24), 1.00, "测试预创建")
        # 沙箱接口一定几率返回None
        if res:
            self.assertIn(res["code"], ["10000", '20000'], msg=res)

    def test_trade_page_pay(self):
        """测试统一下单并支付页面接口"""
        # 接口返回的是URL连接，因此不报错即认为测试通过
        res = self.alipay.pay.trade_page_pay(
            "SO123", 10, "测试")
        self.assertTrue(res)

    def test_trade_orderinfo_sync(self):
        """测试支付宝订单信息同步接口"""
        # 伪造的订单号，交易不存在
        res = self.alipay.pay.trade_orderinfo_sync(self.order_no,
                                                   "12345", "CREDIT_AUTH")
        self.assertEqual(res["code"], "40004", msg=res)

    def test_trade_page_refund(self):
        """测试统一收单退款页面接口"""
        # [FIXME] 沙箱环境返回了错误的方法名，需要验证
        res = self.alipay.pay.trade_page_refund(
            String.generate_digits(24), 1.00, out_trade_no=self.order_no)
        self.assertTrue(res)

    def test_trade_orer_settle(self):
        """测试统一交易结算接口"""
        # [FIXME] 没有分账业务类型
        res = self.alipay.pay.trade_order_settle(String.generate_digits(24), trade_no="2019110822001414381000134139", royalty_parameters=[{
            "trans_in": "2088102179155775"
        }])
        self.assertEqual(res["code"], "40004", res)

    def test_product(self):
        alipay = AliPay("2019091267287120", """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxTxXdQG9+VX1GcU/ETVQHAOIez1el6Vfc2zsXj9Wc3BoU8A29zRDjJPxbZXD0yNQYCzNkLXSnuL9ZDAOtRo5S4XMb92ZhMlEq+yedNSt4qCzEp7eLz+6uwsbNlgAzNlBUynW59kmSHVaCfQx1CkFcFjgZeiVAoJuGa8ujFWiX96h3Ec0MTK8G6uF2+Wl6Tlh8wiShivuw4fcWV4QKxWhTIJ+Dyi2tFszlwt0fJriI12x/xPT0dEr/U2p/8ZhtqlKAKrZJ9fjrGIkM5cSpQcnCEnmZDg6bYfE7NYCQNTIVjM6fXH3Ic1sNXQ5eG0WBRsMrvfiHBqJSU4J9fY1GXy5QQIDAQABAoIBADt9Ssew4dLtmULPmokfMm1wp168kOZea97NsLFwmyuwcNcp96oyKlmhWcV60ZjCYwDPIqWOIdvojRMF57m6EiP0VEg9Z4uEhWDxuo10hIoBfGGWZ1+K8lBuNiP7ASrIMIrb6MT/WyupsaGk9M6QHOLY+73hG+io3HqEux56ycHuRfpX17KU1t6MQzCmcx7C1XixjSsP07+6PW1ya+++1LiRGzRjhv1nu3VWWQyw3hpodbAXDN6CCGt+z+2RYDnqVp5Evq1NLwFe5tU8WDRcLw0eAuRH+wDXG9gO/fryJm51NUHBoaiCa+XkwzeKwc0zp/HGaApbDcSRKkaRAqCwvw0CgYEA5z8pzYoa/xscY2BNAGQFyx+gYErpnoxMYNyPTKHGzkWgvby4pfkMCaEf3v9Ddx5dQiXylCknil/EI5x9rtcdrEbZxsEf6siiNM+KMCMkgJHMXPWNw5zMckiinv0Uu6F5VxJImvoSf0o/J2xjeVZEdWU7OpzKTI8ge0LP9QMSIdMCgYEA2lktRzp3fcIOdUq2HN9077AaRceEYNMVVww9l6tpG8rvOR8T+s6E3Cnu+NkmvQVbZxLDwb5AxNxfMi0h5osfzlyKLfJ5LrGAZT31odxDtjUMfQ93M2vbG72PiGH2gNDO7J07KX1STZEtXQC0s56XiAAbTTuXka1OP1pupKr/OBsCgYEA4B2bShT7LRr9XGLMvgAyjTZNnIV9/adDruyUBVUU9H0O2FS7MEA6pmp+FQWYQS4wfBeDDo0EQVunIExeksDxhTH1hmdNo6Jncn9iEl081052nfFuP5MLogc7dJMbMO3CR9z0eR68Jpmys2ac0dAF8TD3QksK1UAx3sRV/8PGIvkCgYEAy8uqQC4o8z7Z4c3+1koWydSTYQfM3daGt32cS2DYtPEfgTAppNF3HkshWjDMQGasnjLcdYvOxi9txtZrKtQ1tpWW/zWut89CqLxA9Hcy1/EBnASAXIVRt72hJ0lQG4FJcX17h8kJtY5ISeLrxi7C/lQjJ130pSqduvH8DUPw/HsCgYB1mOY7YU0I8H1pXDG3FeBBWAk2Iu4kmzTbACpyiHhSfGDvMOdh7LEnLen5O0rjBteI+B4G5Qo5LcBzemzCsgNTLwbUqMQvU+1onsgHVhZ0u8LcuW06ZLmcHUMqmNBn23xsA6Z3aCZ//z08LJ6w2w6E3nSzy4JUyM62Cn/xSVigPw==
-----END RSA PRIVATE KEY-----""",
                        sign_type="rsa2")
        res = alipay.pay.trade_query(trade_no="2019111022001469351413117626")
        self.assertEqual(res["code"], '40006')

    def test_trade_advance_consult(self):
        """
        测试交易垫资咨询

        沙箱环境缺少对此接口的支持，因此使用正式环境测试
        """

        alipay = AliPay("2019091267287120", """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxTxXdQG9+VX1GcU/ETVQHAOIez1el6Vfc2zsXj9Wc3BoU8A29zRDjJPxbZXD0yNQYCzNkLXSnuL9ZDAOtRo5S4XMb92ZhMlEq+yedNSt4qCzEp7eLz+6uwsbNlgAzNlBUynW59kmSHVaCfQx1CkFcFjgZeiVAoJuGa8ujFWiX96h3Ec0MTK8G6uF2+Wl6Tlh8wiShivuw4fcWV4QKxWhTIJ+Dyi2tFszlwt0fJriI12x/xPT0dEr/U2p/8ZhtqlKAKrZJ9fjrGIkM5cSpQcnCEnmZDg6bYfE7NYCQNTIVjM6fXH3Ic1sNXQ5eG0WBRsMrvfiHBqJSU4J9fY1GXy5QQIDAQABAoIBADt9Ssew4dLtmULPmokfMm1wp168kOZea97NsLFwmyuwcNcp96oyKlmhWcV60ZjCYwDPIqWOIdvojRMF57m6EiP0VEg9Z4uEhWDxuo10hIoBfGGWZ1+K8lBuNiP7ASrIMIrb6MT/WyupsaGk9M6QHOLY+73hG+io3HqEux56ycHuRfpX17KU1t6MQzCmcx7C1XixjSsP07+6PW1ya+++1LiRGzRjhv1nu3VWWQyw3hpodbAXDN6CCGt+z+2RYDnqVp5Evq1NLwFe5tU8WDRcLw0eAuRH+wDXG9gO/fryJm51NUHBoaiCa+XkwzeKwc0zp/HGaApbDcSRKkaRAqCwvw0CgYEA5z8pzYoa/xscY2BNAGQFyx+gYErpnoxMYNyPTKHGzkWgvby4pfkMCaEf3v9Ddx5dQiXylCknil/EI5x9rtcdrEbZxsEf6siiNM+KMCMkgJHMXPWNw5zMckiinv0Uu6F5VxJImvoSf0o/J2xjeVZEdWU7OpzKTI8ge0LP9QMSIdMCgYEA2lktRzp3fcIOdUq2HN9077AaRceEYNMVVww9l6tpG8rvOR8T+s6E3Cnu+NkmvQVbZxLDwb5AxNxfMi0h5osfzlyKLfJ5LrGAZT31odxDtjUMfQ93M2vbG72PiGH2gNDO7J07KX1STZEtXQC0s56XiAAbTTuXka1OP1pupKr/OBsCgYEA4B2bShT7LRr9XGLMvgAyjTZNnIV9/adDruyUBVUU9H0O2FS7MEA6pmp+FQWYQS4wfBeDDo0EQVunIExeksDxhTH1hmdNo6Jncn9iEl081052nfFuP5MLogc7dJMbMO3CR9z0eR68Jpmys2ac0dAF8TD3QksK1UAx3sRV/8PGIvkCgYEAy8uqQC4o8z7Z4c3+1koWydSTYQfM3daGt32cS2DYtPEfgTAppNF3HkshWjDMQGasnjLcdYvOxi9txtZrKtQ1tpWW/zWut89CqLxA9Hcy1/EBnASAXIVRt72hJ0lQG4FJcX17h8kJtY5ISeLrxi7C/lQjJ130pSqduvH8DUPw/HsCgYB1mOY7YU0I8H1pXDG3FeBBWAk2Iu4kmzTbACpyiHhSfGDvMOdh7LEnLen5O0rjBteI+B4G5Qo5LcBzemzCsgNTLwbUqMQvU+1onsgHVhZ0u8LcuW06ZLmcHUMqmNBn23xsA6Z3aCZ//z08LJ6w2w6E3nSzy4JUyM62Cn/xSVigPw==
-----END RSA PRIVATE KEY-----""",
                        sign_type="rsa2")

        res = alipay.pay.trade_advance_consult("2088302483540171", industry_product_code="CAR_OWNERS_PARKINGPAY",
                                               sub_merchant_id="2088102122458832", sub_merchant_type="PARTNER")
        self.assertEqual(res['code'], '40006')

    def test_trade_wap_pay(self):
        """
        测试 手机网站支付接口2.0

        沙箱环境不支持
        """
        pass

    def test_commerce_transport_nfccard_send(self):
        """
        测试NFC用户卡信息同步

        沙箱环境不支持本接口
        """

        alipay = AliPay("2019091267287120", """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAxTxXdQG9+VX1GcU/ETVQHAOIez1el6Vfc2zsXj9Wc3BoU8A29zRDjJPxbZXD0yNQYCzNkLXSnuL9ZDAOtRo5S4XMb92ZhMlEq+yedNSt4qCzEp7eLz+6uwsbNlgAzNlBUynW59kmSHVaCfQx1CkFcFjgZeiVAoJuGa8ujFWiX96h3Ec0MTK8G6uF2+Wl6Tlh8wiShivuw4fcWV4QKxWhTIJ+Dyi2tFszlwt0fJriI12x/xPT0dEr/U2p/8ZhtqlKAKrZJ9fjrGIkM5cSpQcnCEnmZDg6bYfE7NYCQNTIVjM6fXH3Ic1sNXQ5eG0WBRsMrvfiHBqJSU4J9fY1GXy5QQIDAQABAoIBADt9Ssew4dLtmULPmokfMm1wp168kOZea97NsLFwmyuwcNcp96oyKlmhWcV60ZjCYwDPIqWOIdvojRMF57m6EiP0VEg9Z4uEhWDxuo10hIoBfGGWZ1+K8lBuNiP7ASrIMIrb6MT/WyupsaGk9M6QHOLY+73hG+io3HqEux56ycHuRfpX17KU1t6MQzCmcx7C1XixjSsP07+6PW1ya+++1LiRGzRjhv1nu3VWWQyw3hpodbAXDN6CCGt+z+2RYDnqVp5Evq1NLwFe5tU8WDRcLw0eAuRH+wDXG9gO/fryJm51NUHBoaiCa+XkwzeKwc0zp/HGaApbDcSRKkaRAqCwvw0CgYEA5z8pzYoa/xscY2BNAGQFyx+gYErpnoxMYNyPTKHGzkWgvby4pfkMCaEf3v9Ddx5dQiXylCknil/EI5x9rtcdrEbZxsEf6siiNM+KMCMkgJHMXPWNw5zMckiinv0Uu6F5VxJImvoSf0o/J2xjeVZEdWU7OpzKTI8ge0LP9QMSIdMCgYEA2lktRzp3fcIOdUq2HN9077AaRceEYNMVVww9l6tpG8rvOR8T+s6E3Cnu+NkmvQVbZxLDwb5AxNxfMi0h5osfzlyKLfJ5LrGAZT31odxDtjUMfQ93M2vbG72PiGH2gNDO7J07KX1STZEtXQC0s56XiAAbTTuXka1OP1pupKr/OBsCgYEA4B2bShT7LRr9XGLMvgAyjTZNnIV9/adDruyUBVUU9H0O2FS7MEA6pmp+FQWYQS4wfBeDDo0EQVunIExeksDxhTH1hmdNo6Jncn9iEl081052nfFuP5MLogc7dJMbMO3CR9z0eR68Jpmys2ac0dAF8TD3QksK1UAx3sRV/8PGIvkCgYEAy8uqQC4o8z7Z4c3+1koWydSTYQfM3daGt32cS2DYtPEfgTAppNF3HkshWjDMQGasnjLcdYvOxi9txtZrKtQ1tpWW/zWut89CqLxA9Hcy1/EBnASAXIVRt72hJ0lQG4FJcX17h8kJtY5ISeLrxi7C/lQjJ130pSqduvH8DUPw/HsCgYB1mOY7YU0I8H1pXDG3FeBBWAk2Iu4kmzTbACpyiHhSfGDvMOdh7LEnLen5O0rjBteI+B4G5Qo5LcBzemzCsgNTLwbUqMQvU+1onsgHVhZ0u8LcuW06ZLmcHUMqmNBn23xsA6Z3aCZ//z08LJ6w2w6E3nSzy4JUyM62Cn/xSVigPw==
-----END RSA PRIVATE KEY-----""",
                        sign_type="rsa2")

        res = alipay.pay.commerce_transport_nfccard_send(
            "12345678", "12345678", "CANCEL")
        self.assertEqual(res['code'], '40006')



if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(TestPay("test_trade_create"))
    # suite.addTest(TestPay("test_trade_close"))
    # suite.addTest(TestPay("test_trade_query"))
    # suite.addTest(TestPay("test_trade_refund"))
    # suite.addTest(TestPay("test_precreate"))
    # suite.addTest(TestPay("test_trade_page_pay"))
    # suite.addTest(TestPay("test_trade_orderinfo_sync"))
    # suite.addTest(TestPay("test_trade_page_refund"))
    # suite.addTest(TestPay("test_product"))
    # suite.addTest(TestPay("test_trade_advance_consult"))
    # suite.addTest(TestPay("test_trade_wap_pay"))
    suite.addTest(TestPay("test_commerce_transport_nfccard_send"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
