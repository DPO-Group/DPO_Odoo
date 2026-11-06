# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

import re
import unicodedata
import xml.etree.ElementTree as ET

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import urls

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment.logging import get_payment_logger
from odoo.addons.payment_dpo.controllers.main import DPOController

_logger = get_payment_logger(__name__)


def _ascii(value):
    """ Strip accents and non-ASCII characters DPO rejects in address fields. """
    if not value:
        return ''
    value = re.sub(r"º", "o", value)
    return ''.join(c for c in unicodedata.normalize('NFD', value) if unicodedata.category(c) != 'Mn')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    dpo_transaction_token = fields.Char(string="DPO Transaction Token", copy=False, readonly=True)

    def _get_specific_rendering_values(self, processing_values):
        """ Override of `payment_dpo` to use the configurable pay URL. """
        if self.provider_code != 'dpo':
            return super()._get_specific_rendering_values(processing_values)

        token = self._dpo_create_token()
        pay_url = self.provider_id.dpo_pay_url or 'https://secure.3gdirectpay.com/payv3.php'
        return {'api_url': f'{pay_url}?ID={token}'}

    def _dpo_build_create_token_payload(self):
        """ Build the createToken request. Values are XML-escaped by ElementTree. """
        self.ensure_one()
        provider = self.provider_id
        return_url = urls.urljoin(provider.get_base_url(), DPOController._return_url)
        first_name, last_name = payment_utils.split_partner_name(self.partner_name)
        mobile = ''.join(re.findall(r"\d+", self.partner_phone or ''))

        root = ET.Element('API3G')
        ET.SubElement(root, 'CompanyToken').text = provider.dpo_company_token
        ET.SubElement(root, 'Request').text = 'createToken'
        tx = ET.SubElement(root, 'Transaction')
        for tag, text in (
            ('PaymentAmount', f'{self.amount:.2f}'),
            ('PaymentCurrency', self.currency_id.name),
            ('CompanyRef', self.reference),
            ('RedirectURL', return_url),
            ('BackURL', return_url),
            ('CompanyRefUnique', '0'),
            ('customerFirstName', first_name),
            ('customerLastName', last_name),
            ('customerAddress', _ascii(self.partner_address)),
            ('customerCity', self.partner_city or ''),
            ('customerCountry', self.partner_country_id.code or ''),
            ('customerEmail', self.partner_email or ''),
            ('customerPhone', mobile),
            ('customerZip', self.partner_zip or ''),
        ):
            ET.SubElement(tx, tag).text = text
        if provider.dpo_payment_time_limit:
            ET.SubElement(tx, 'PTL').text = str(provider.dpo_payment_time_limit)

        service = ET.SubElement(ET.SubElement(root, 'Services'), 'Service')
        ET.SubElement(service, 'ServiceType').text = provider.dpo_service_ref
        ET.SubElement(service, 'ServiceDescription').text = provider.dpo_service_description or self.reference
        ET.SubElement(service, 'ServiceDate').text = self.create_date.strftime('%Y/%m/%d %H:%M')

        blocked = [code for flag, code in (
            (provider.dpo_block_bank_transfer, 'BT'), (provider.dpo_block_paypal, 'PP'),
        ) if flag]
        if blocked:
            additional = ET.SubElement(root, 'Additional')
            for code in blocked:
                ET.SubElement(additional, 'BlockPayment').text = code

        return ET.tostring(root, encoding='unicode', xml_declaration=False)

    def _dpo_create_token(self):
        """ Override of `payment_dpo` to send the extended createToken request. """
        self.ensure_one()
        payload = '<?xml version="1.0" encoding="utf-8"?>' + self._dpo_build_create_token_payload()
        # A ValidationError rolls back the request, so surface DPO's explanation to the customer
        # instead of recording an error state that would be rolled back with it.
        data = self._send_api_request('POST', '', data=payload)
        if data.get('Result') not in (None, '000') or not data.get('TransToken'):
            raise ValidationError(_("DPO: %s", data.get('ResultExplanation') or data.get('Result')))
        self.dpo_transaction_token = data['TransToken']
        return data['TransToken']

    def _dpo_verify_token(self, token):
        """ Ask DPO for the status of a payment and return the parsed response. """
        self.ensure_one()
        root = ET.Element('API3G')
        ET.SubElement(root, 'CompanyToken').text = self.provider_id.dpo_company_token
        ET.SubElement(root, 'Request').text = 'verifyToken'
        ET.SubElement(root, 'TransactionToken').text = token
        payload = '<?xml version="1.0" encoding="utf-8"?>' + ET.tostring(root, encoding='unicode')
        return self._send_api_request('POST', '', data=payload)

    def _extract_amount_data(self, payment_data):
        """ Override of `payment_dpo` to not crash when DPO returns no amount.

        A missing amount makes Odoo set the transaction in error ("amount or currency is missing") instead of
        raising an HTTP 500.
        """
        if self.provider_code != 'dpo':
            return super()._extract_amount_data(payment_data)
        amount = (payment_data.get('TransactionAmount') or '').replace(',', '')
        return {
            'amount': float(amount) if amount else 0.0,
            'currency_code': payment_data.get('TransactionCurrency'),
        }
