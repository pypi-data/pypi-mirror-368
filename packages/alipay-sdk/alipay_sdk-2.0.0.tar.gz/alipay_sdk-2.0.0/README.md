![alipay](alipay.png)

[![Build Status](https://travis-ci.org/block-cat/alipay_sdk.svg?branch=master)](https://travis-ci.org/block-cat/alipay_sdk)
[![Coverage Status](https://coveralls.io/repos/github/block-cat/alipay_sdk/badge.svg?branch=master)](https://coveralls.io/github/block-cat/alipay_sdk?branch=master)
![PyPI](https://img.shields.io/pypi/v/alipay_sdk)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/block-cat/alipay_sdk)


支付宝第三方 Python SDK

# About

由于官方sdk有很大的嫌疑是从java拷贝过来的，因此，重新起了这个项目

### Main functionalities

* 支付功能
* 口碑功能

> 由于沙箱环境缺少口碑权限支持，仅定义了接口功能，未进行完整的单元测试

更多功能正在开发中...

### Requirements

python >= 3.6

### Install

```
pip install alipay_sdk
```

### How to use

首先要到[支付宝开放平台](https://openhome.alipay.com/)注册一个开发者账号，并创建一个应用并获取应用ID(AppID)。

通知需要配置应用密钥、商户密钥和支付宝公钥，详情参考[官方文档](https://docs.open.alipay.com/291/105971/)

假设我们的AppId是12345，商户密钥文件是1.txt，支付宝公钥是2.txt
那么我们的可以这么使用：

```python
with open("1.txt", "r") as f:
    private_key = RSA.importKey(f.read())
with open("2.txt", "r") as f:
    publick_key = RSA.importKey(f.read())
alipay = Alipay("12345",private_key,private_key,
    sign_type="rsa2", ali_public_key=publick_key)
```

> 0.0.3 版本起，支持直接传入密钥文本

注意：支付宝公钥等可以使用官方提供的工具生成，但是对于非java平台的语言，需要补齐密钥格式中的格式头：

```txt
-----BEGIN RSA PRIVATE KEY-----
..........
-----END RSA PRIVATE KEY-----
```

接下来就可以使用sdk来调用接口了，以统一下单接口为例：

```python
res = alipay.pay.trade_create(self.alipay.pay.trade_create(
        "5489763229687797", 1.01, "测试统一下单", buyer_id="208810217951438X"))
```
