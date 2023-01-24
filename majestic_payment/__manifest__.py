# -*- coding: utf-8 -*-
{
    'name': "majestic_payment",
    'depends': ['base','payment', 'account', 'purchase'],
    # always loaded
    'data': [
        'views/views.xml',
        'views/purchase_payment_view.xml',
        'reports/report_view.xml',
    ],
}
