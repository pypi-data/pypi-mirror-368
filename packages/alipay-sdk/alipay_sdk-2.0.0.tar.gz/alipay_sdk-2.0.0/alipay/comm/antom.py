#!/usr/bin/python3
# @Time    : 2024-05-15
# @Author  : Kevin Kong (kfx2007@163.com)

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256, SHA
from Crypto.PublicKey import RSA
import base64
import time
import json
import requests
from urllib.parse import quote_plus, quote


class AntomCore(object):
    def __get__(self, instance, type):
        self.private_key = instance.private_key
        self.client_id = instance.client_id
        self.url = instance.url
        return self

    def build_sign_string(self, method, uri, client_id, timestamp, data):
        s = f"""{method} {uri}\n{client_id}.{timestamp}.{data}"""
        return s

    def sign(self, s, private_key=None):
        if private_key is None:
            private_key = self.private_key

        to_sign = SHA256.new(s.encode("utf-8"))
        base64str = base64.b64encode(PKCS1_v1_5.new(private_key).sign(to_sign)).decode(
            "utf-8"
        )
        return quote_plus(base64str)

    def build_headers(self, signature, data, timestamp=None):
        headers = {
            "Content-type": "application/json; charset=UTF-8",
            "Accept": "text/plain,text/xml,text/javascript,text/html",
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
            "User-Agent": "global-alipay-sdk-python",
            "Request-Time": timestamp if timestamp else str(int(time.time())),
            "client-id": self.client_id,
            "Signature": f"algorithm=RSA256,keyVersion=1,signature={signature}",
        }
        return headers

    def post(self, endpoint, data):
        data = json.dumps(
            {key: value for key, value in data.items() if value is not None}
        )
        url, timestamp = f"/ams/sandbox/api/{endpoint}", str(int(time.time()))
        sign_str = self.build_sign_string("POST", url, self.client_id, timestamp, data)
        signature = self.sign(sign_str)
        headers = self.build_headers(signature, data, timestamp=timestamp)
        return requests.post(f"{self.url}{url}", data=data, headers=headers).json()
