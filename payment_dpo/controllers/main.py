#
# Copyright (c) 2023 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

import logging
import pprint

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DPOController(http.Controller):

    @http.route('/payment/dpo/return', type='http', auth="public", methods=['GET'])
    def dpo_return_from_redirect(self, **data):
        """ DPO Pay return """
        _logger.info("received DPO Pay return data:\n%s", pprint.pformat(data))
        request.env['payment.transaction'].sudo()._handle_notification_data('dpo', data)
        return request.redirect('/payment/status')
