# -*- coding: utf-8 -*-
# 
# Copyright (c) 2024 DPO Group (Pty) Ltd
#
# Author: App Inlet (Pty) Ltd
#
# Released under the GNU General Public License
#

{
    'name': "DPO Pay Payment Gateway",
    'version': '17.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'DPO Pay Gateway Integration for Odoo 17',
    'description': 'DPO Pay Payment Gateway Integration for Odoo 17, dpo, payment gateway, Payment Gateway Integration, dpo payment, odoo 17, odoo payment gateway',
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
