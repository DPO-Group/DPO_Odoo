# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

from urllib.parse import urlsplit

from odoo import fields, models

DPO_DEFAULT_PAY_URL = 'https://secure.3gdirectpay.com/payv3.php'


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    dpo_pay_url = fields.Char(
        string="Pay URL",
        default=DPO_DEFAULT_PAY_URL,
        help="The DPO payment page the customer is redirected to. The API endpoint is derived from its host.",
    )
    dpo_service_description = fields.Char(
        string="Service Description",
        default="Goods and services",
        help="The service description sent to DPO. Falls back to the transaction reference when empty.",
    )
    dpo_block_bank_transfer = fields.Boolean(string="Block Bank Transfer", default=True)
    dpo_block_paypal = fields.Boolean(string="Block PayPal", default=True)
    dpo_payment_time_limit = fields.Integer(
        string="Payment Time Limit (hours)",
        default=5,
        help="How long the DPO payment page stays valid (PTL). Leave 0 to use the DPO default.",
    )

    def _build_request_url(self, endpoint, **kwargs):
        """ Override of `payment_dpo` to derive the API endpoint from the configured pay URL host. """
        url = super()._build_request_url(endpoint, **kwargs)
        if self.code != 'dpo' or not self.dpo_pay_url:
            return url
        parts = urlsplit(self.dpo_pay_url)
        if not parts.scheme or not parts.netloc:
            return url
        return f'{parts.scheme}://{parts.netloc}/API/v6/'
