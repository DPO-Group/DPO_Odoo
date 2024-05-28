#
# Copyright (c) 2024 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('dpo', "DPO")], ondelete={'dpo': 'set default'})
    dpo_company_token = fields.Char("Company Token", required_if_provider='dpo')
    dpo_service_type = fields.Char("Service Type", required_if_provider='dpo')
    dpo_service_description = fields.Char("Service Description")
    dpo_pay_url = fields.Char("Pay URL", required_if_provider='dpo')
    display_as = fields.Char("DPO Pay")
    support_fees = fields.Char("Support Fees")

    def _get_default_payment_method_id(self, *_args):
        self.ensure_one()
        if self.code != 'dpo':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_dpo.payment_method_dpo').id

