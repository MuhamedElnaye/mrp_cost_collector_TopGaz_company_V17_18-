{
    'name': "MRP Cost Collector",
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': " Calculate and analyze cost of components for muliple finished product",
    'description': """
          This module allows the user to:
        - Select multiple finished products
        - Input desired quantities
        - Aggregate BOMs
        - Compare with current stock
        - Calculate the cost of missing components

    """,
    'author': 'Eng/Mohamed Elgarhy and Eng/Mohamed El-Nayed',
    'depends': ['base','mail','mrp','stock','purchase','sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/cost_collector_view.xml',
        'views/partner_balance_view.xml',
        'views/cost_collector_export_wizard.xml',
        'report/cost_collector_report.xml',
        'report/sale_orders_report.xml',
        'report/sale_orders_report11.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False
}