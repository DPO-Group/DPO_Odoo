# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#
from odoo import api, models


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['dpo'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
