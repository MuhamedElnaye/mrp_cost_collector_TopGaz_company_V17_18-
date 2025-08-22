import io
import base64
import xlsxwriter

from odoo import models, fields, api

class CostCollectorExportWizard(models.TransientModel):
    _name = 'mrp.cost.collector.export.wizard'
    _description = 'Export Components Wizard'

    field_product = fields.Boolean(string='Component', default=True)
    field_required = fields.Boolean(string='Required Qty', default=True)
    field_available = fields.Boolean(string='Available Qty', default=True)
    field_missing = fields.Boolean(string='Missing Qty', default=True)
    field_cost = fields.Boolean(string='Unit Cost', default=True)
    field_total = fields.Boolean(string='Total Cost', default=True)

    collector_id = fields.Many2one('mrp.cost.collector', string="Collector")

    def export_selected_fields(self):
        fields_to_export = []
        headers = []
        if self.field_product:
            fields_to_export.append('product_id')
            headers.append('Component')
        if self.field_required:
            fields_to_export.append('required_qty')
            headers.append('Required Qty')
        if self.field_available:
            fields_to_export.append('available_qty')
            headers.append('Available Qty')
        if self.field_missing:
            fields_to_export.append('missing_qty')
            headers.append('Missing Qty')
        if self.field_cost:
            fields_to_export.append('purchase_cost')
            headers.append('Unit Cost')
        if self.field_total:
            fields_to_export.append('total_cost')
            headers.append('Total Cost')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet("Components")
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#a3193c', 'color': 'white', 'border': 1, 'align': 'center'})

        for record in self.collector_id:
            if record.only_lines_with_cost:
                lines = record.component_line_ids.filtered(lambda line: line.total_cost > 0)
            else:
                lines = record.component_line_ids

        for col, header in enumerate(headers):
            sheet.write(1, col + 1, header, header_format)
        string_format = workbook.add_format({'border': 1, 'align': 'center'})
        # price_format = workbook.add_format({"num_format": "$##,##00.00", 'border': 1, 'align': 'center'})
        row = 2
        for line in lines:
            col = 1
            for field in fields_to_export:
                value = getattr(line, field)
                if hasattr(value, 'display_name'):
                    value = value.display_name
                sheet.write(row, col, value, string_format)
                col += 1
            row += 1

        workbook.close()
        output.seek(0)
        xlsx_data = output.read()

        attachment = self.env['ir.attachment'].create({
            'name': 'Components_Custom.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(xlsx_data),
            'res_model': 'mrp.cost.collector',
            'res_id': self.collector_id.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
