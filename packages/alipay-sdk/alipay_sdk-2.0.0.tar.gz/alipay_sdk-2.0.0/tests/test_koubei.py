#!/usr/bin/python3
# @Time    : 2019-11-27
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from Crypto.PublicKey import RSA
from alipay.api import AliPay


class KoubeiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(KoubeiTest, cls).setUpClass()
        with open("private.txt", "r") as f:
            private_key = RSA.importKey(f.read())
        cls.alipay = AliPay("2016101100664659", private_key,
                            sign_type="rsa2", sandbox=True)
        cls.buyer_id = "2088102179514385"

    def test_koubei_trade_itemorder_query(self):
        """
        测试口碑商品交易查询接口
        """
        res = self.alipay.koubei.trade_itemorder_query("123456")
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_koubei_trade_itemorder_buy(self):
        """
        测试口碑商品交易购买接口
        """
        res = self.alipay.koubei.trade_itemorder_buy(
            "11223344", "测试口碑购买", "ABC", "测试场景", "1", "abcde", 20)
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_koubei_trade_itemorder_refund(self):
        """
        测试口碑商品交易退货接口
        """
        res = self.alipay.koubei.trade_itemorder_refund(
            "11223344", "00000", {"item_order_no": "12312", "amount": 10})
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_koubei_trade_ticket_ticketcode_send(self):
        """
        测试码商发码成功回调接口
        """
        res = self.alipay.koubei.trade_ticket_ticketcode_send([{
            "code": "11111",
            "num": 1
        }], "AAAAA", "xsoekt", "kborder001")
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_trade_ticket_ticketcode_delay(self):
        """
        测试口碑凭证延期接口
        """
        res = self.alipay.koubei.trade_ticket_ticketcode_delay(
            '2020-12-31', "123456", "111222333")
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_trade_order_precreate(self):
        """
        测试口碑订单预下单
        """
        res = self.alipay.koubei.trade_order_precreate("1112233", "12")
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_trade_ticket_ticketcode_query(self):
        """
        测试口碑凭证码查询
        """
        res = self.alipay.koubei.trade_ticket_ticketcode_query("1111", "222")
        self.assertIn(res['code'], ['40006'], msg=res)

    def test_trade_ticket_ticketcode_cancel(self):
        """
        测试口碑凭证码撤销核销
        """
        res = self.alipay.koubei.trade_ticket_ticketcode_cancel("111111","22222","33333")
        self.assertIn(res['code'], ['40006'], msg=res)

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(KoubeiTest("test_koubei_trade_itemorder_query"))
    suite.addTest(KoubeiTest("test_koubei_trade_itemorder_buy"))
    suite.addTest(KoubeiTest("test_koubei_trade_itemorder_refund"))
    suite.addTest(KoubeiTest("test_koubei_trade_ticket_ticketcode_send"))
    suite.addTest(KoubeiTest("test_trade_ticket_ticketcode_delay"))
    suite.addTest(KoubeiTest("test_trade_order_precreate"))
    suite.addTest(KoubeiTest("test_trade_ticket_ticketcode_query"))
    suite.addTest(KoubeiTest("test_trade_ticket_ticketcode_cancel"))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
