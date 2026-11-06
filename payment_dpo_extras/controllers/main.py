# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.payment_dpo.controllers.main import DPOController

_logger = get_payment_logger(__name__)


class DPOControllerExtras(DPOController):

    @staticmethod
    def _verify_and_process(data):
        """ Override of `payment_dpo` to verify the payment with the transaction token.

        Odoo's version verifies with the `TransID` of the return URL. DPO's payv3 page returns the numeric
        transaction id there, which `verifyToken` rejects (result 902), so the payment was never confirmed.
        The token created at `createToken` time is used instead, with the `TransactionToken` of the return URL
        as a fallback.
        """
        tx_sudo = request.env['payment.transaction'].sudo()._search_by_reference('dpo', data)
        if not tx_sudo:
            return

        token = tx_sudo.dpo_transaction_token or data.get('TransactionToken') or data.get('TransID')
        try:
            verified_data = tx_sudo._dpo_verify_token(token)
        except ValidationError:
            _logger.error("Unable to verify the DPO payment data for transaction %s.", tx_sudo.reference)
            return
        data.update(verified_data)
        tx_sudo._process('dpo', data)
