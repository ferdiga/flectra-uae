# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2014 Tech Receptives (<http://techreceptives.com>)

{
    'name': 'U.A.E. - Accounting',
    'author': 'Tech Receptives',
    'category': 'Accounting/Localizations/Account Charts',
    'description': """
United Arab Emirates accounting chart and localization.
=======================================================
20230104 ChriCar: for tax exempt companies all items including Tax must be supressed in invoices.
         A tax exempt company has no entry in res.partner.vat
    """,
    'depends': ['base', 'account'],
    'data': [
             'data/l10n_ae_data.xml',
             'data/account_data.xml',
             'data/l10n_ae_chart_data.xml',
             'data/account.account.template.csv',
             'data/l10n_ae_chart_post_data.xml',
             'data/account_tax_report_data.xml',
             'data/account_tax_template_data.xml',
             'data/fiscal_templates_data.xml',
             'data/account_chart_template_data.xml',
             'views/report_invoice_templates.xml',
    ],
    'demo': [
        'demo/demo_company.xml',
    ],
    'license': 'LGPL-3',
}
