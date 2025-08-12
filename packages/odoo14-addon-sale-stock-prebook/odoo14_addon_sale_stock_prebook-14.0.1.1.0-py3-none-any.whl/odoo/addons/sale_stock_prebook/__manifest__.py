# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Sale Stock Prebook",
    "summary": "Add process to prebook a sale order's stock before confirming it",
    "version": "14.0.1.1.0",
    "author": "MT Software, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/sale-prebook",
    "data": [
        "views/sale_views.xml",
        "views/stock_location_route_views.xml",
    ],
    "depends": [
        "sale_stock",
    ],
    "maintainers": ["mt-software-de"],
    "license": "LGPL-3",
    "pre_init_hook": "pre_init_hook",
}
