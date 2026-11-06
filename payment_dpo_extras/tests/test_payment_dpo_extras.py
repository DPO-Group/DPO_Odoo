# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestDpoExtras(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env['payment.provider'].search([('code', '=', 'dpo')], limit=1)
        cls.provider.write({
            'dpo_company_token': 'TOKEN-123',
            'dpo_service_ref': '54841',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Jan van der Merwe & Sons',
            'email': 'jan@example.com',
            'phone': '+27 (82) 123-4567',
            'street': 'Straße 1º',
            'city': 'Pretoria',
            'zip': '0001',
            'country_id': cls.env.ref('base.za').id,
        })
        method = cls.env['payment.method'].with_context(active_test=False).search([('code', '=', 'dpo')], limit=1)
        cls.tx = cls.env['payment.transaction'].create({
            'provider_id': cls.provider.id,
            'payment_method_id': method.id,
            'amount': 99.5,
            'currency_id': cls.env.ref('base.ZAR').id,
            'partner_id': cls.partner.id,
            'reference': 'S0001-1',
            'operation': 'online_redirect',
        })

    def _payload(self):
        return ET.fromstring(self.tx._dpo_build_create_token_payload())

    def test_payload_contains_extras_and_escapes(self):
        root = self._payload()
        self.assertEqual(root.findtext('CompanyToken'), 'TOKEN-123')
        tx = root.find('Transaction')
        self.assertEqual(tx.findtext('PaymentAmount'), '99.50')
        self.assertEqual(tx.findtext('PaymentCurrency'), 'ZAR')
        self.assertEqual(tx.findtext('customerPhone'), '27821234567')
        self.assertEqual(tx.findtext('customerAddress'), 'Straße 1o')
        self.assertEqual(tx.findtext('customerCountry'), 'ZA')
        self.assertEqual(tx.findtext('PTL'), '5')
        self.assertEqual(tx.findtext('customerLastName'), 'Sons')
        svc = root.find('Services/Service')
        self.assertEqual(svc.findtext('ServiceType'), '54841')
        self.assertEqual(svc.findtext('ServiceDescription'), 'Goods and services')
        self.assertEqual([e.text for e in root.findall('Additional/BlockPayment')], ['BT', 'PP'])

    def test_options_can_be_switched_off(self):
        self.provider.write({
            'dpo_block_bank_transfer': False,
            'dpo_block_paypal': False,
            'dpo_payment_time_limit': 0,
            'dpo_service_description': False,
        })
        root = self._payload()
        self.assertIsNone(root.find('Additional'))
        self.assertIsNone(root.find('Transaction/PTL'))
        self.assertEqual(root.findtext('Services/Service/ServiceDescription'), 'S0001-1')

    def test_api_url_derived_from_pay_url(self):
        self.provider.dpo_pay_url = 'https://sandbox.example.com/payv3.php'
        self.assertEqual(self.provider._build_request_url(''), 'https://sandbox.example.com/API/v6/')

    def test_redirect_url_uses_pay_url_and_token(self):
        with patch.object(type(self.tx), '_send_api_request',
                          return_value={'Result': '000', 'TransToken': 'ABC'}):
            vals = self.tx._get_specific_rendering_values({})
        self.assertEqual(vals['api_url'], 'https://secure.3gdirectpay.com/payv3.php?ID=ABC')

    def test_dpo_refusal_raises_with_explanation(self):
        with patch.object(type(self.tx), '_send_api_request',
                          return_value={'Result': '904', 'ResultExplanation': 'Request missing company token'}):
            with self.assertRaisesRegex(ValidationError, 'Request missing company token'):
                self.tx._get_specific_rendering_values({})

    def test_verify_token_uses_given_token_in_payload(self):
        captured = {}

        def fake(self_, method, endpoint, **kwargs):
            captured['data'] = kwargs['data']
            return {'Result': '000', 'TransactionAmount': '99.50', 'TransactionCurrency': 'ZAR'}

        with patch.object(type(self.tx), '_send_api_request', fake):
            res = self.tx._dpo_verify_token('1A30851A-TOKEN')
        root = ET.fromstring(captured['data'].split('?>', 1)[1])
        self.assertEqual(root.findtext('Request'), 'verifyToken')
        self.assertEqual(root.findtext('TransactionToken'), '1A30851A-TOKEN')
        self.assertEqual(res['Result'], '000')

    def test_create_token_stores_transaction_token(self):
        with patch.object(type(self.tx), '_send_api_request',
                          return_value={'Result': '000', 'TransToken': 'GUID-1'}):
            self.tx._dpo_create_token()
        self.assertEqual(self.tx.dpo_transaction_token, 'GUID-1')

    def test_missing_amount_does_not_crash_and_sets_error(self):
        self.tx._set_pending()
        data = {'CompanyRef': 'S0001-1', 'Result': '902', 'ResultExplanation': 'Wrong transactionToken'}
        self.assertEqual(self.tx._extract_amount_data(data)['amount'], 0.0)
        self.env['payment.transaction']._process('dpo', data)
        self.assertEqual(self.tx.state, 'error')

    def test_done_payment_is_processed(self):
        self.tx._set_pending()
        data = {'CompanyRef': 'S0001-1', 'Result': '000', 'TransID': '1',
                'TransactionAmount': '99.50', 'TransactionCurrency': 'ZAR'}
        self.env['payment.transaction']._process('dpo', data)
        self.assertEqual(self.tx.state, 'done')
