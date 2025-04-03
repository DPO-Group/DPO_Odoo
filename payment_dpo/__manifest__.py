# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

{
    'name': "DPO Pay Payment Gateway",
    'version': '18.0.1.0.1',
    'category': 'eCommerce',
    'summary': 'DPO Pay Gateway Integration for Odoo 18',
    'description': 'DPO Pay Payment Gateway Integration for Odoo 18, dpo, payment gateway, Payment Gateway Integration, dpo payment, odoo 18, odoo payment gateway',
    'author': 'App Inlet (Pty) Ltd',
    'company': 'DPO Group (Pty) Ltd',
    'maintainer': 'App Inlet (Pty) Ltd',
    'images': ['static/description/banner.gif'],
    'website': 'https://dpogroup.com',
    'depends': ['payment'],
    'data': [
        'views/payment_dpo_templates.xml',
        'views/payment_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'license': 'GPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
