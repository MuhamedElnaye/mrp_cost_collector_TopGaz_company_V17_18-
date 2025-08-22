from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def print_fawry_invoice(self):
        return self.env.ref('mrp_cost_collector.sale_orders_report').report_action(self)

    def print_fawry_invoice11(self):
        return self.env.ref('mrp_cost_collector.sale_orders_report11').report_action(self)