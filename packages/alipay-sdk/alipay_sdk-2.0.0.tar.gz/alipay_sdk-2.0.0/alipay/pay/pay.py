#!/usr/bin/python3
# @Time    : 2019-10-31
# @Author  : Kevin Kong (kfx2007@163.com)

# 支付宝当面付
# 包含 条码支付、扫码支付两个业务场景

from functools import partial
from alipay.comm import Comm, isp_args

alipay = partial(isp_args, method='alipay')


class Pay(Comm):

    @alipay
    def trade_create(self, out_trade_no, total_amount, subject,
                     body=None, buyer_id=None, discountable_amount=None, seller_id=None,
                     goods_detail=None, product_code="FACE_TO_FACE_PAYMENT", operator_id=None, store_id=None, terminal_id=None,
                     extend_params=None, timeout_express=None, settle_info=None, logistics_detail=None, business_params=None,
                     receiver_address_info=None):
        """
        统一收单交易创建接口
        """
        return self.post()

    @alipay
    def trade_pay(self, out_trade_no, scene, auth_code, subject,
                  product_code=None, buyer_id=None, seller_id=None,
                  total_amount=None, trans_currency=None, settle_currency=None,
                  discountable_amount=None, body=None, goods_detail=None,
                  operator_id=None, store_id=None, terminal_id=None,
                  extend_params=None, timeout_express=None, auth_confirm_mode=None,
                  terminal_params=None, promo_params=None, advance_payment_type=None):
        """
        统一收单交易支付接口
        参数：
            out_trade_no: string 商户订单号 64个字符以内
            scene： string 支付场景 (bar_code,wave_code) 32 
            auth_code: string 支付授权码 32 
            subject: string 订单标题 32
            product_code: string 产品码 32
            buyer_id: string 买家支付宝id 28
            seller_id: string 卖家支付宝id 28
            total_amount: float 订单总金额 11 
            trans_currency: string 币种
            settle_currency: string 商户结算币种
            discountable_amount：float 参与优惠计算的金额，单位为元，精确到小数点后两位
            body: string 订单描述
            goods_detail: list 订单包含的商品列表信息，json格式
            operator_id: string 商户操作员编号
            store_id: string 商户门店编号
            terminal_id: string 商户机具终端编号
            extend_params: dict 业务扩展参数
            timeout_express: string 该笔订单允许的最晚付款时间，逾期将关闭交易。
            auth_confirm_mode: string 预授权确认模式，授权转交易请求中传入，适用于预授权转交易业务使用，目前只支持PRE_AUTH(预授权产品码)
            terminal_params: 商户传入终端设备相关信息，具体值要和支付宝约定
            promo_params: 优惠明细参数，通过此属性补充营销参数
            advance_payment_type: 支付模式类型,若值为ENJOY_PAY_V2表示当前交易允许走先享后付2.0垫资
        """
        return self.post()

    @alipay
    def trade_close(self, trade_no=None, out_trade_no=None, operator_id=None):
        """
        统一收单交易关闭接口
        参数：
            trade_no： string 64 该交易在支付宝系统中的交易流水号
            out_trade_no: string 64 订单支付时传入的商户订单号,和支付宝交易号不能同时为空
            operator_id: 卖家端自定义的的操作员 ID
        """
        if not trade_no and not out_trade_no:
            raise Exception("交易流水号和商户订单号不能同时为空")
        return self.post()

    @alipay
    def trade_query(self, out_trade_no=None, trade_no=None, org_pid=None, query_options=None):
        """
        统一收单线下交易查询
        参数：
            out_trade_no：string 订单支付时传入的商户订单号,和支付宝交易号不能同时为空。
            trade_no：string 支付宝交易号，和商户订单号不能同时为空
            org_pid：string 银行间联模式下有用，其它场景请不要使用
            query_options： string 查询选项，商户通过上送该字段来定制查询返回信息
        """
        if not trade_no and not out_trade_no:
            raise Exception("交易流水号和商户订单号不能同时为空")
        return self.post()

    @alipay
    def trade_refund(self, refund_amount, out_trade_no=None, trade_no=None,
                     refund_currency=None, refund_reason=None, out_request_no=None,
                     operator_id=None, store_id=None, terminal_id=None, goods_detail=None,
                     refund_royalty_parameters=None):
        """
        统一收单交易退款接口
        参数：
            refund_amount: float 需要退款的金额，该金额不能大于订单金额,单位为元，支持两位小数 
            out_trade_no： string 64 订单支付时传入的商户订单号,不能和 trade_no同时为空
            trade_no： string   64 支付宝交易号，和商户订单号不能同时为空
            refund_currency: string 8 订单退款币种信息
            refund_reason: string 256  退款的原因说明
            out_request_no: string 64 标识一次退款请求，同一笔交易多次退款需要保证唯一，如需部分退款，则此参数必传
            operator_id: string 30 商户的操作员编号
            store_id: string 32 商户的门店编号
            terminal_id: string 32 商户的终端编号
            goods_detail: list 退款包含的商品列表信息，Json格式。其它说明详见 https://docs.open.alipay.com/api_1/alipay.trade.refund
            refund_royalty_parameters: dict 退分账明细信息
            org_pid: string 16 银行间联模式下有用，其它场景请不要使用；双联通过该参数指定需要退款的交易所属收单机构的pid;
        """
        if not trade_no and not out_trade_no:
            raise Exception("支付宝交易号，和商户订单号不能同时为空")
        return self.post()

    @alipay
    def trade_fastpay_refund_query(self, out_request_no, trade_no=None, out_trade_no=None, org_pid=None):
        """
        统一收单交易退款查询
        参数：
            trade_no: string 64 支付宝交易号，和商户订单号不能同时为空
            out_trade_no:  string 64 订单支付时传入的商户订单号,和支付宝交易号不能同时为空
            out_request_no: string 64 请求退款接口时，传入的退款请求号，如果在退款请求时未传入，则该值为创建交易时的外部交易号
            org_pid: string 16 银行间联模式下有用，其它场景请不要使用；双联通过该参数指定需要退款的交易所属收单机构的pid;
        """
        if not trade_no and not out_trade_no:
            raise Exception("支付宝交易号，和商户订单号不能同时为空")
        return self.post()

    @alipay
    def trade_precreate(self, out_trade_no, total_amount, subject,
                        goods_detail=None, discountable_amount=None,
                        seller_id=None, body=None, product_code=None,
                        operator_id=None, store_id=None, disable_pay_channels=None,
                        enable_pay_channels=None, terminal_id=None, extend_params=None,
                        timeout_express=None, settle_info=None, merchant_order_no=None,
                        business_params=None, qr_code_timeout_express=None):
        """
        统一收单线下交易预创建
        收银员通过收银台或商户后台调用支付宝接口，生成二维码后，展示给用户，由用户扫描二维码完成订单支付。
        参数：
            out_trade_no: string 64 商户订单号,64个字符以内、只能包含字母、数字、下划线；需保证在商户端不重复
            total_amount: float 订单总金额，单位为元，精确到小数点后两位
            subject: string 256 订单标题
            goods_detail: list 订单包含的商品列表信息.json格式. 其它说明详见：“商品明细说明”
            discountable_amount: float 可打折金额. 参与优惠计算的金额，单位为元，精确到小数点后两位
            seller_id: string 28 卖家支付宝用户ID。 如果该值为空，则默认为商户签约账号对应的支付宝用户ID
            body: string 128 对交易或商品的描述
            product_code: 销售产品码。
            operator_id: 商户操作员编号
            store_id: 商户门店编号
            disable_pay_channels:禁用渠道，用户不可用指定渠道支付当有多个渠道时用“,”分隔注，与enable_pay_channels互斥渠道列表：https://docs.open.alipay.com/common/wifww7
            enable_pay_channels: string 128 可用渠道，用户只能在指定渠道范围内支付当有多个渠道时用“,”分隔注，与disable_pay_channels互斥渠道列表
            terminal_id: string 32 商户机具终端编号
            extend_params: dict 业务扩展参数 详细信息参考 https://docs.open.alipay.com/api_1/alipay.trade.precreate/
            timeout_express: string 32 该笔订单允许的最晚付款时间，逾期将关闭交易。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m
            settle_info: json 描述结算信息，json格式，详见结算参数说明
            merchant_order_no: string 32 商户原始订单号，最大长度限制32位
            business_params: json 商户传入业务信息，具体值要和支付宝约定，应用于安全，营销等参数直传场景，格式为json格式
            qr_code_timeout_express: string 6 该笔订单允许的最晚付款时间，逾期将关闭交易，从生成二维码开始计时。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m。
        """
        return self.post()

    @alipay
    def trade_cancel(self, out_trade_no=None, trade_no=None):
        """
        统一收单交易撤销接口
        支付交易返回失败或支付系统超时，调用该接口撤销交易。
        如果此订单用户支付失败，支付宝系统会将此订单关闭；
        如果用户支付成功，支付宝系统会将此订单资金退还给用户。 
        注意：只有发生支付系统超时或者支付结果未知时可调用撤销，其他正常支付的单如需实现相同功能请调用申请退款API。
        提交支付交易后调用【查询订单API】，没有明确的支付结果再调用【撤销订单API】
        """
        if not trade_no and not out_trade_no:
            raise Exception("支付宝交易号，和商户订单号不能同时为空")
        return self.post()

    @alipay
    def trade_page_pay(self, out_trade_no, total_amount, subject, product_code="FAST_INSTANT_TRADE_PAY",
                       body=None, time_expire=None, goods_detail=None, passback_params=None, extend_params=None,
                       goods_type=None, timeout_express=None, promo_params=None, royalty_info=None, sub_merchant=None,
                       merchant_order_no=None, enable_pay_channels=None, store_id=None, disable_pay_channels=None,
                       qr_pay_mode=None, qrcode_width=None, settle_info=None, invoice_info=None,
                       agreement_sign_params=None, integration_type=None, request_from_url=None,
                       business_params=None, ext_user_info=None):
        """
        统一收单下单并支付页面接口
        参数：
            out_trade_no: string 64 商户订单号,64个字符以内、可包含字母、数字、下划线
            total_amount: float 订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]
            subject: string 256 订单标题
            product_code: string 64 销售产品码，与支付宝签约的产品码名称。注：目前仅支持FAST_INSTANT_TRADE_PAY
            body: string 128 订单描述
            time_expire： string 32 绝对超时时间，格式为yyyy-MM-dd HH:mm:ss
            goods_detail: list 订单包含的商品列表信息，json格式，其它说明详见商品明细说明
            passback_params: string 512 公用回传参数，如果请求时传递了该参数，则返回给商户时会回传该参数。支付宝只会在同步返回（包括跳转回商户网站）和异步通知时将该参数原样返回。本参数必须进行UrlEncode之后才可以发送给支付宝
            extend_params: dict 业务扩展参数
            goods_type: string 2 商品主类型 :0-虚拟类商品,1-实物类商品 注：虚拟类商品不支持使用花呗渠道
            timeout_express: string 6 该笔订单允许的最晚付款时间，逾期将关闭交易。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m
            promo_params: string 512 优惠参数 注：仅与支付宝协商后可用
            royalty_info: json 描述分账信息，json格式，详见分账参数说明
            sub_merchant: json 间连受理商户信息体，当前只对特殊银行机构特定场景下使用此字段
            merchant_order_no: string 32 商户原始订单号，最大长度限制32位
            enable_pay_channels: string 128 可用渠道,用户只能在指定渠道范围内支付，多个渠道以逗号分割 注，与disable_pay_channels互斥 渠道列表：https://docs.open.alipay.com/common/wifww7 
            store_id: string 32 商户门店编号
            disable_pay_channels: string 128 禁用渠道,用户不可用指定渠道支付，多个渠道以逗号分割 注，与enable_pay_channels互斥
            qr_pay_mode: string 2 PC扫码支付的方式，支持前置模式和跳转模式。
                0：订单码-简约前置模式，对应 iframe 宽度不能小于600px，高度不能小于300px；
                1：订单码-前置模式，对应iframe 宽度不能小于 300px，高度不能小于600px；
                2：订单码-跳转模式
                3：订单码-迷你前置模式，对应 iframe 宽度不能小于 75px，高度不能小于75px；
                4：订单码-可定义宽度的嵌入式二维码，商户可根据需要设定二维码的大小。
            qrcode_width: int 商户自定义二维码宽度 注：qr_pay_mode=4时该参数生效
            settle_info: json 描述结算信息，json格式，详见结算参数说明
            invoice_info: json 开票信息	
            agreement_sign_params: 签约参数，支付后签约场景使用
            integration_type: string 16 请求后页面的集成方式。取值范围：1. ALIAPP：支付宝钱包内 2. PCWEB：PC端访问
            request_from_url: string 256 请求来源地址。如果使用ALIAPP的集成方式，用户中途取消支付会返回该地址。
            business_params: string 512 商户传入业务信息，具体值要和支付宝约定，应用于安全，营销等参数直传场景，格式为json格式
            ext_user_info: json 外部指定买家
        返回：
            拼接好的URL,由应用程序直接发起请求即可
        """
        return self._get_request_url()

    @alipay
    def trade_orderinfo_sync(self, trade_no, out_request_no, biz_type, orig_request_no=None, order_biz_info=None):
        """
        支付宝订单信息同步接口
        该接口用于商户向支付宝同步该笔订单相关业务信息
        参数：
            trade_no: string 64 支付宝交易号
            out_request_no: string 64 标识一笔交易多次请求，同一笔交易多次信息同步时需要保证唯一
            biz_type: string 64 交易信息同步对应的业务类型，具体值与支付宝约定；
                                信用授权场景下传CREDIT_AUTH
                                信用代扣场景下传CREDIT_DEDUCT
            orig_request_no: string 64 原始业务请求单号。如对某一次退款进行履约时，该字段传退款时的退款请求号
            order_biz_info: string 2018 商户传入同步信息，具体值要和支付宝约定；用于芝麻信用租车、单次授权等信息同步场景，格式为json格式。
        """
        return self.post()

    @alipay
    def trade_page_refund(self, out_request_no, refund_amount,
                          trade_no=None, out_trade_no=None, biz_type=None,
                          refund_reason=None, operator_id=None, store_id=None,
                          terminal_id=None, extend_params=None):
        """
        统一收单退款页面接口
        当交易发生之后一段时间内，由于买家或者卖家的原因需要退款时，卖家可以通过退款页面接口将支付款退还给买家，支付宝将在收到退款请求并且验证成功之后，按照退款规则将支付款按原路退到买家帐号上。 目前该接口用于信用退款场景，通过biz_type指定信用退款。支付宝页面会提示用户退款成功或失败，退款处理完成后支付宝回跳到商户请求指定的回跳地址页面。
        参数：
            out_request_no: string 64 标识一次退款请求，同一笔交易多次退款需要保证唯一
            refund_amount: float 需要退款的金额，该金额不能大于订单金额,单位为元，支持两位小数
            trade_no: string 64 支付宝交易号，和商户订单号不能同时为空
            out_trade_no: string 64 支付宝交易号，和商户订单号不能同时为空
            biz_type: string 32 退款场景。信用退款传CREDIT_REFUND；
            refund_reason: string 256 退款的原因说明
            operator_id: string 30 商户的操作员编号
            store_id: string 32 商户的门店编号
            terminal_id: string 32 商户的终端编号
            extend_params: json 	业务扩展参数
        详情参考： https://docs.open.alipay.com/api_1/alipay.trade.page.refund
        返回：
            退款页面，应用程序直接请求即可
        """
        if not trade_no and not out_trade_no:
            raise Exception("支付宝交易号，和商户订单号不能同时为空")
        return self._get_request_url()

    @alipay
    def trade_order_settle(self, out_request_no, trade_no, royalty_parameters, operator_id=None):
        """
        统一收单交易结算接口
        用于在线下场景交易支付后，进行卖家与第三方（如供应商或平台商）基于交易金额的结算。
        参数：
            out_request_no：string 64 结算请求流水号 开发者自行生成并保证唯一性
            trade_no：string 64 支付宝订单号
            royalty_parameters: Array 分账明细信息 详情参考：https://docs.open.alipay.com/api_1/alipay.trade.order.settle/
            operator_id：string 64 操作员id
        """
        return self.post()

    @alipay
    def trade_advance_consult(self, alipay_user_id, industry_product_code=None,
                              sub_merchant_id=None, sub_merchant_type=None):
        """
        交易垫资咨询

        商户通过此接口咨询，当前用户是否满足垫资服务条件

        :param alipay_user_id: 必选	32	支付宝用户id	
        :param industry_product_code: 可选	128	行业产品信息，咨询是，会从该产品对应的销售方案中获取相关垫资规则配置	
        :param sub_merchant_id: 可选	64	子商户id	
        :param sub_merchant_type: 可选	64	子商户类型
        :return: 返回数据
        """

        return self.post()

    @alipay
    def trade_wap_pay(self, subject, out_trade_no, total_amount, quit_url, product_code,
                      body=None, timeout_express=None,
                      time_expire=None, auth_token=None, goods_type='0',
                      passback_params=None, promo_params=None, ExtendParams=None,
                      merchant_order_no=None, enable_pay_channels=None, disable_pay_channels=None,
                      store_id=None, specified_channel=None, business_params=None, ext_user_info=None):
        """
        手机网站支付接口2.0

        外部商户创建订单并支付

        :param subject: 必选	256	商品的标题/交易标题/订单标题/订单关键字等。
        :param out_trade_no: 必选	64	商户网站唯一订单号
        :param total_amount: 必选	9	订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]
        :param quit_url: 必选	400	用户付款中途退出返回商户网站的地址
        :param product_code: 必选	64	销售产品码，商家和支付宝签约的产品码
        :param body: 可选	128	对一笔交易的具体描述信息。如果是多种商品，请将商品描述字符串累加传给body。
        :param timeout_express: 可选	该笔订单允许的最晚付款时间，逾期将关闭交易。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m。
        :param time_expire: 可选	32	绝对超时时间，格式为yyyy-MM-dd HH:mm
        :param auth_token: 可选	40	针对用户授权接口，获取用户相关数据时，用于标识用户授权关系
        :param goods_type: 可选	2	商品主类型 :0-虚拟类商品,1-实物类商品 默认为0
        :param passback_params: 可选	512	公用回传参数，如果请求时传递了该参数，则返回给商户时会回传该参数。支付宝只会在同步返回（包括跳转回商户网站）和异步通知时将该参数原样返回。本参数必须进行UrlEncode之后才可以发送给支付宝。
        :param promo_params: 可选	512	优惠参数 注：仅与支付宝协商后可用
        :param extend_params: 可选		业务扩展参数 https://docs.open.alipay.com/api_1/alipay.trade.wap.pay/
        :param merchant_order_no: 可选	32	商户原始订单号，最大长度限制32位
        :param enable_pay_channels: 可选	128	可用渠道，用户只能在指定渠道范围内支付 当有多个渠道时用“,”分隔 注，与disable_pay_channels互斥
        :param disable_pay_channels: 可选	128	禁用渠道，用户不可用指定渠道支付 当有多个渠道时用“,”分隔 注，与enable_pay_channels互斥
        :param store_id: 商户门店编号
        :param specified_channel: 指定渠道，目前仅支持传入pcredit 若由于用户原因渠道不可用，用户可选择是否用其他渠道支付。
        :param business_params: 可选	512	商户传入业务信息，具体值要和支付宝约定，应用于安全，营销等参数直传场景，格式为json格式
        :param ext_user_info: 可选		外部指定买家
        :return：返回数据
        """

        return self.post()

    @alipay
    def commerce_transport_nfccard_send(self, issue_org_no, card_no, card_status):
        """
        NFC用户卡信息同步

        当NFC卡状态或信息发生变更时，可通过该服务同步到支付宝

        :param issue_org_no: 必选	32	发卡机构代码
        :param card_no: 必选	128	卡号
        :param card_status: 必选	16	卡片状态（FREEZE：冻结，CANCEL：销卡）	
        :return：返回数据
        """

        return self.post()

    @alipay
    def pcredit_huabei_auth_settle_apply(self, agreement_no, pay_amount, out_request_no, alipay_user_id,
                                         seller_id=None, need_terminated=None, extend_params=None):
        """
        花芝轻会员结算申请

        用户已经开通花芝轻会员协议后，商户通过此接口解冻转支付用户冻结金额。传入金额必须小于等于冻结金额

        :param agreement_no:支付宝系统中用以唯一标识用户签约记录的编号。
        :param pay_amount:需要支付的金额，单位为：元（人民币），精确到小数点后两位
        :param out_request_no:商户本次操作的请求流水号，用于标示请求流水的唯一性，不能包含除中文、英文、数字以外的字符，需要保证在商户端不重复。
        :param alipay_user_id:买家在支付宝的用户id
        :param seller_id: 商户的支付宝用户id。如果该值为空，则默认为商户签约账号对应的支付宝用户ID。
        :param extend_params: 业务扩展参数
        :return: 返回结果
        """

        return self.post()

    @alipay
    def fund_auth_order_freeze(self, auth_code, auth_code_type, out_order_no, out_request_no,
                               order_title, amount, product_code, payee_logon_id=None, payee_user_id=None,
                               pay_timeout=None, extra_param=None, trans_currency=None, settle_currency=None,
                               scene_code=None, terminal_params=None, enable_pay_channels=None, identity_params=None):
        """
        资金授权冻结接口

        收银员使用扫码设备读取用户支付宝钱包“付款码”后，将条码信息和订单信息通过本接口上送至支付宝发起资金冻结。

        :param auth_code: 支付授权码，25~30开头的长度为16~24位的数字，实际字符串长度以开发者获取的付款码长度为准
        :param auth_code_type: 授权码类型 目前支持"bar_code"和"security_code"，分别对应付款码和刷脸场景
        :param out_order_no: 商户授权资金订单号 ,不能包含除中文、英文、数字以外的字符，创建后不能修改，需要保证在商户端不重复
        :param out_request_no: 商户本次资金操作的请求流水号，用于标示请求流水的唯一性，不能包含除中文、英文、数字以外的字符，需要保证在商户端不重复
        :param order_title: 业务订单的简单描述，如商品名称等长度不超过100个字母或50个汉字
        :param amount: 需要冻结的金额，单位为：元（人民币），精确到小数点后两位 取值范围：[0.01,100000000.00]
        :param product_code: 销售产品码，后续新接入预授权当面付的业务，新当面资金授权取值PRE_AUTH，境外预授权取值OVERSEAS_INSTORE_AUTH。
        :param payee_logon_id: 收款方支付宝账号（Email或手机号），如果收款方支付宝登录号(payee_logon_id)和用户号(payee_user_id)同时传递，则以用户号(payee_user_id)为准，如果商户有勾选花呗渠道，收款方支付宝登录号(payee_logon_id)和用户号(payee_user_id)不能同时为空。
        :param payee_user_id: 收款方的支付宝唯一用户号,以2088开头的16位纯数字组成，如果非空则会在支付时校验交易的的收款方与此是否一致，如果商户有勾选花呗渠道，收款方支付宝登录号(payee_logon_id)和用户号(payee_user_id)不能同时为空
        :param pay_timeout: 该笔订单允许的最晚付款时间，逾期将关闭该笔订单
                            取值范围：1m～15d。m-分钟，h-小时，d-天。 该参数数值不接受小数点， 如 1.5h，可转换为90m
                            如果为空，默认15m
        :param extra_param: 业务扩展参数，用于商户的特定业务信息的传递，json格式。
                            1.间联模式必须传入二级商户ID，key为secondaryMerchantId;
                            2. 当面资金授权业务对应的类目，key为category，value由支付宝分配，酒店业务传 "HOTEL"；
                            3. 外部商户的门店编号，key为outStoreCode，可选；
                            4. 外部商户的门店简称，key为outStoreAlias，可选
        :param payee_user_id: 标价币种, amount 对应的币种单位。支持澳元：AUD, 新西兰元：NZD, 台币：TWD, 美元：USD, 欧元：EUR, 英镑：GBP
        :param settle_currency: 商户指定的结算币种。支持澳元：AUD, 新西兰元：NZD, 台币：TWD, 美元：USD, 欧元：EUR, 英镑：GBP
        :param scene_code: 场景码，预授权刷脸场景取值为HOTEL，其他不需填写
        :param terminal_params: 机具管控sdk加签参数，参数示例 "terminal_params":"{"terminalType":"IOT","signature":"QIIAX8DqbFbNf2oe97FI1RSLAycC/tU4GVjer3bN8K4qLtAB","apdidToken":"xPA3ptuArwYc3F6Va_pjVwv7Qx7Tg5TJdrA_Jb_moYte9AqGZgEAAA==","hardToken":"","time":"1539847253","bizCode":"11000200040004000121","bizTid":"010100F01i1XyacMgpOinHerfdBw1xA9dNDocctlnqhLD8lfODr1A7Q","signedKeys":"authCode,totalAmount,apdidToken,hardToken,time,bizCode,bizTid"}"
        :param enable_pay_channels:商户可用该参数指定用户可使用的支付渠道，本期支持商户可支持三种支付渠道，余额宝（MONEY_FUND）、花呗（PCREDIT_PAY）以及芝麻信用（CREDITZHIMA）。商户可设置一种支付渠道，也可设置多种支付渠道。
        :param identity_params:用户实名信息参数，包含：姓名+身份证号的hash值、指定用户的uid。商户传入用户实名信息参数，支付宝会对比用户在支付宝端的实名信息。
                                姓名+身份证号hash值使用SHA256摘要方式与UTF8编码,返回十六进制的字符串。
                                identity_hash和alipay_user_id都是可选的，如果两个都传，则会先校验identity_hash，然后校验alipay_user_id。其中identity_hash的待加密字样如"张三4566498798498498498498"

        :return: 返回结果
        """

        if not payee_logon_id and not payee_user_id:
            raise ValueError("收款方支付宝账号和用户号不能同时为空")
        return self.post()

    @alipay
    def alipay_trade_app_pay(self, total_amount, subject, out_trade_no,
                             timeout_express=None, product_code=None, body=None,
                             time_expire=None, goods_type=None, promo_params=None, passback_params=None,
                             extend_params=None, merchant_order_no=None, enable_pay_channels=None,
                             store_id=None, specified_channel=None, disable_pay_channels=None, goods_detail=None,
                             ext_user_info=None,):
        """
        app支付接口2.0

        外部商户APP唤起快捷SDK创建订单并支付

        :param total_amount: 订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]
        :param subject: 商品的标题/交易标题/订单标题/订单关键字等。
        :param out_trade_no: 商户网站唯一订单号
        :param timeout_express: 该笔订单允许的最晚付款时间，逾期将关闭交易。取值范围：1m～15d。m-分钟，h-小时，d-天，1c-当天（1c-当天的情况下，无论交易何时创建，都在0点关闭）。 该参数数值不接受小数点， 如 1.5h，可转换为 90m
        :param product_code: 销售产品码，商家和支付宝签约的产品码
        :param body: 对一笔交易的具体描述信息。如果是多种商品，请将商品描述字符串累加传给body。
        :param time_expire: 绝对超时时间，格式为yyyy-MM-dd HH:mm。
        :param goods_type: 商品主类型 :0-虚拟类商品,1-实物类商品
        :param promo_params: 优惠参数 注：仅与支付宝协商后可用
        :param passback_params: 公用回传参数，如果请求时传递了该参数，则返回给商户时会回传该参数。支付宝只会在同步返回（包括跳转回商户网站）和异步通知时将该参数原样返回。本参数必须进行UrlEncode之后才可以发送给支付宝。
        :param extend_params: 业务扩展参数
        :param merchant_order_no: 商户原始订单号，最大长度限制32位
        :param enable_pay_channels: 可用渠道，用户只能在指定渠道范围内支付
                                    当有多个渠道时用“,”分隔
                                    注，与disable_pay_channels互斥
        :param store_id: 商户门店编号
        :param specified_channel: 指定渠道，目前仅支持传入pcredit
                                  若由于用户原因渠道不可用，用户可选择是否用其他渠道支付。
                                  注：该参数不可与花呗分期参数同时传入
        :param disable_pay_channels: 禁用渠道，用户不可用指定渠道支付
                                     当有多个渠道时用“,”分隔 注，与enable_pay_channels互斥
        :param goods_detail: 订单包含的商品列表信息，json格式，其它说明详见商品明细说明
        :param ext_user_info: 外部指定买家
        :param business_params: 商户传入业务信息，具体值要和支付宝约定，应用于安全，营销等参数直传场景，格式为json格式
        :param agreement_sign_params: 签约参数。如果希望在sdk中支付并签约，需要在这里传入签约信息
        :return 返回结果
        """

        self.post()
