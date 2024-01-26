#
# Copyright (c) 2024 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

import http.client
import requests
import logging
import re
import unicodedata

import xml.etree.ElementTree as ET
from datetime import datetime

from odoo import models, _, api, fields
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from werkzeug import urls

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    dpo_payment_token = fields.Char()

    def prepare_address(self, values):
    
        values = re.sub(r"º", "o", values)
      
        return ''.join(c for c in unicodedata.normalize('NFD', values)
                        if unicodedata.category(c) != 'Mn')

    def get_dpo_token(self, values):
        conn = http.client.HTTPSConnection("secure.3gdirectpay.com")

        base_url = self.provider_id.get_base_url()
        return_url = urls.url_join(base_url, '/payment/dpo/return')
        back_url = urls.url_join(base_url, '/payment/dpo/return')

        partner_id = self.env['res.partner'].browse(values['partner_id'])
        currency_id = self.env['res.currency'].browse(values['currency_id'])
        mobile = ''
        if partner_id.phone:
            match = re.findall(r"\d+", partner_id.phone)
            mobile = ''.join(match)
        name = partner_id.name.split()
        partner_street = self.prepare_address(partner_id.street) or ''
        payload = f"""<?xml version="1.0" encoding="utf-8"?> <API3G> <CompanyToken>{self.provider_id.dpo_company_token}</CompanyToken> <Request>createToken</Request> <Transaction> <PaymentAmount>{values['amount']}</PaymentAmount> <PaymentCurrency>{currency_id.name}</PaymentCurrency> <CompanyRef>{values['reference']}</CompanyRef> <RedirectURL>{return_url}</RedirectURL> <BackURL>{back_url}</BackURL> <CompanyRefUnique>0</CompanyRefUnique> <customerFirstName>{name[0]}</customerFirstName> <customerLastName>{name[-1]}</customerLastName> <customerAddress>{partner_street}</customerAddress> <customerCity>{partner_id.city}</customerCity> <customerCountry>{partner_id.country_id.code}</customerCountry> <customerEmail>{partner_id.email or ''}</customerEmail> <customerPhone>{mobile}</customerPhone> <customerZip>{partner_id.zip or ''}</customerZip> <PTL>5</PTL> </Transaction> <Services> <Service> <ServiceType>{self.provider_id.dpo_service_type}</ServiceType> <ServiceDescription>{self.provider_id.dpo_service_description}</ServiceDescription> <ServiceDate>{datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M')}</ServiceDate> </Service> </Services> <Additional> <BlockPayment>BT</BlockPayment> <BlockPayment>PP</BlockPayment> </Additional> </API3G>"""
        _logger.info(payload)
        headers = {
            'Content-Type': 'application/xml'
        }
        url = self.provider_id.dpo_pay_url or 'https://secure.3gdirectpay.com/payv3.php'
        url += '/API/v6/'
        res = requests.post(url, data=payload, headers=headers)
        data = res.content
        _logger.info(data)
        tree = ET.ElementTree(ET.fromstring(data.decode("utf-8")))
        response = {i.tag: i.text for i in tree.getroot()}
        return response

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'dpo':
            return res
        if not self.provider_id.dpo_pay_url:
            raise ValidationError("Setup DPO url first then try again.")
        api_url = self.provider_id.dpo_pay_url + '?ID={}'
        response = self.get_dpo_token(processing_values)
        _logger.info(response)
        self.dpo_payment_token = response['TransToken']
        rendering_values = {
            'api_url': api_url.format(self.dpo_payment_token),
        }
        return rendering_values

    @api.model
    def _get_tx_from_notification_data(self, provider, data):
        tx = super()._get_tx_from_notification_data(provider, data)
        if provider != 'dpo':
            return tx

        reference = data.get('CompanyRef')
        CCDapproval = data.get('CCDapproval')

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'dpo')])
        if not tx:
            raise ValidationError(
                "DPO: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, data):
        super()._process_notification_data(data)
        if self.provider_code != 'dpo':
            return

        response = self.dpo_verify_token()

        self.provider_reference = data.get('TransactionToken')
        status = response.get('Result')

        if data.get('PnrID') == self.reference:
            if status in ['007', '003']:
                self._set_pending(response.get('ResultExplanation'))
            elif status in ['001', '005']:
                self._set_authorized(response.get('ResultExplanation'))
            elif status in ['000', '001', '002']:
                self._set_done()
            elif status in ['801', '802', '803', '804', ]:
                self._set_error(response.get('ResultExplanation'))
            elif status in ['900', '901', '902', '903', '904', '950']:
                self._set_canceled(response.get('ResultExplanation'))
        else:
            _logger.info(
                "received invalid transaction status for transaction with reference %s: %s",
                self.reference, status
            )
            self._set_error("DPO: " + _("received invalid transaction status: %s", status))

    def dpo_verify_token(self):
        payload = f"""
        <?xml version="1.0" encoding="utf-8"?>
        <API3G>
          <CompanyToken>{self.provider_id.dpo_company_token}</CompanyToken>
          <Request>verifyToken</Request>
          <TransactionToken>{self.dpo_payment_token}</TransactionToken>
        </API3G>
        """
        headers = {
            'Content-Type': 'application/xml'
        }
        url = self.provider_id.dpo_pay_url or 'https://secure.3gdirectpay.com/payv3.php'
        url += '/API/v6/'
        res = requests.post(url, data=payload, headers=headers)
        data = res.content
        tree = ET.ElementTree(ET.fromstring(data.decode("utf-8")))
        response = {i.tag: i.text for i in tree.getroot()}
        return response
