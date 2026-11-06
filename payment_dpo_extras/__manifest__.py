# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

{
    'name': "DPO Pay Extras",
    'version': '19.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Extra DPO Pay options on top of the built-in Odoo 19 DPO payment provider',
    'description': 'Extends the DPO payment provider that ships with Odoo 19 with a configurable pay URL, '
                   'service description, customer address and phone, blocked payment methods and a payment time '
                   'limit. Requires no replacement of the built-in module.',
    'author': 'App Inlet (Pty) Ltd',
    'company': 'DPO Group (Pty) Ltd',
    'maintainer': 'App Inlet (Pty) Ltd',
    'website': 'https://dpogroup.com',
    'depends': ['payment_dpo'],
    'data': [
        'views/payment_provider_views.xml',
    ],
    'license': 'GPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
