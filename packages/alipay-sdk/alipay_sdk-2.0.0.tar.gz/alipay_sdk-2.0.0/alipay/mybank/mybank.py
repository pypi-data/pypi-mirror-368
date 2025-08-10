#!/usr/bin/python3
# @Time    : 2019-11-29
# @Author  : Kevin Kong (kfx2007@163.com)

# 网商银行接口

from functools import partial
from alipay.comm import Comm, isp_args

mybank = partial(isp_args, method='mybank')


class MyBank(Comm):

    @mybank
    def payment_trade_order_create(self, partner_id, out_trade_no, recon_related_no,
                                   pd_code, ev_code, total_amount, currency_code,
                                   goods_info, seller_id, pay_type, pay_date,
                                   remark=None):
        """
        网商银行全渠道收单业务订单创建

        外部机构调此接口完成业务单创建

        :param partner_id: 网商合作伙伴ID	
        :param out_trade_no: 外部商户业务订单号	
        :param recon_related_no: 对账关联ID，用以对账时关联网商与对账方订单的唯一ID。(支付单号、支付流水等能够串联两边订单的唯一ID均可作为对账关联ID)	
        :param pd_code: 业务产品码	
        :param ev_code: 业务事件码	
        :param total_amount: 订单总金额，单位为分，取值范围[1,100000000]	
        :param currency_code: 币种值	
        :param goods_info: 商品信息	
        :param seller_id: 卖家终端ID	
        :param pay_type: 支付类型。pay:支付；refund:退款
        :param pay_date: 支付时间，格式"yyyy-MM-dd HH:mm:ss"
        :param remark: 	交易备注	
        :return: 返回数据
        """

        return self.post()
