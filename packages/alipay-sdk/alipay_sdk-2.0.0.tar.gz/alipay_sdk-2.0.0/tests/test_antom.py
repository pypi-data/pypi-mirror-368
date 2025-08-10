#!/usr/bin/python3
# @Time    : 2024-05-15
# @Author  : Kevin Kong (kfx2007@163.com)

from alipay.comm import AntomCore
from alipay.api import Antom
import unittest
from Crypto.PublicKey import RSA
import json


class TestAntom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestAntom, cls).setUpClass()
        with open("atom.txt") as f:
            private_key = RSA.importKey(f.read())
        cls.antom = Antom("SANDBOX_5YBX442ZG77N01601", private_key)

    def test_sign(self):
        uri = "/ams/api/v1/risk/payments/decide"
        timestamp = "2024-05-16T13:39:25+08:00"
        data = json.dumps({"a": "1"})
        sign_str = self.antom.comm.build_sign_string(
            "POST", uri, self.antom.client_id, timestamp, data
        )
        signature = self.antom.comm.sign(sign_str)
        valid_sign = "lg%2B4t17YISWYRMXJNgBfUZF8IaPNkQgP15VFIHq1TxI7njVy5A%2B%2Fz3sAnJfMUSGs15ufUur0Qf7nUxiZr5%2BGZfEWom%2Bo0Po8VJf17GuSi2qD7EkEs9MpLCUtxrCc3Cuck3pa7xYwF7LWlt58sDNnvsvb4PCCpLsCvV7BZxqAL2zNXo%2FGceekUTobfJqVphcu6aH1sCWElEvwUUmZu2Cu4yMz5o8EzP7AoT0B7B7fbxGFSvPg5qlmVd7jpYIqgp%2FTzbgAfQMq%2BO3mYoUv2ZTAuK0WQhixVBCgg75uHBWUmUHXMWIREIlEKwOh7nhUFsv%2BHGrgJyvMLNb1hSddCjh5%2BA%3D%3D"
        self.assertEqual(signature, valid_sign, signature)

    def test_authorization(self):
        args = {
            "customerBelongsTo": "ALIPAY_CN",
            "authRedirectUrl": "https://www.alipay.com",
            "authState": "STATE_696174270716",
            "osType": "ANDROID",
            "scopes": ["AGREEMENT_PAY"],
            "terminalType": "WEB",
        }
        res = self.antom.auth.consult(**args)
        self.assertEqual(res["result"]["resultCode"], "SUCCESS", res)

    def test_pay(self):
        args = {
            "env": {"osType": "ANDROID", "terminalType": "APP"},
            "order": {
                "merchant": {"referenceMerchantId": "SM_001"},
                "orderAmount": {"currency": "CNY", "value": "1314"},
                "orderDescription": "Cappuccino #grande (Mika's coffee shop)",
                "referenceOrderId": "ORDER_0656237919440XXXX",
            },
            "paymentAmount": {"currency": "CNY", "value": "1314"},
            "paymentMethod": {"paymentMethodType": "ALIPAY_CN"},
            "paymentNotifyUrl": "https://www.gaga.com/notify",
            "paymentRedirectUrl": "imeituan://",
            "paymentRequestId": "Mbu1XMcI8TsH6oIVbioGeyvXA544N9UTIeHJ0YMTLYhRomPU0n7Je2cp3kiCADbp",
            "productCode": "CASHIER_PAYMENT",
            "settlementStrategy": {"settlementCurrency": "USD"},
        }
        res = self.antom.payment.pay(**args)
        
        self.assertIn(res['result']["resultStatus"], ["U", "S"], res)


if __name__ == "__main__":
    unittest.main()
