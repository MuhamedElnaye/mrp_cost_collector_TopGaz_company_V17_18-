from odoo import models, fields, api
from odoo.exceptions import ValidationError
from collections import defaultdict
from odoo.fields import Datetime


class MrpCostCollector(models.Model):
    _name = 'mrp.cost.collector'
    _description = 'Mrp Cost Collector Wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'ref'

    name = fields.Char(default='Planning collector Costs')
    ref = fields.Char(string='Order Reference', default='New', readonly=True)
    date_time = fields.Datetime(string='Date Time', store=True, tracking=1, readonly=True)
    finished_product_ids = fields.Many2many('product.product', string='Products', tracking=1)

    component_line_ids = fields.One2many('mrp.cost.collector.line', 'order_id',
                                         string='Required Product Components')
    global_qty = fields.Char(string='Quantities (e.g 3-2-1)', default='1.0', tracking=1)

    # location_id = fields.Many2one('res.users', string='Responsible',tracking=1)
    # location_id = fields.Many2one('stock.location', string='Responsible', tracking=1)
    location_ids = fields.Many2many('stock.location', string='Responsible', tracking=1)

    total_cost_all = fields.Float(string="Total Cost Of Required Component", compute="_compute_total_cost_all",
                                  store=True)
    #----------------------------------------------
    #----------------------------------------------
    total_cost_all_with_currency = fields.Char(
        string='Total Cost Of Required Component',
        compute='_compute_total_cost_all_with_currency',
        store=True,
    )
    only_lines_with_cost = fields.Boolean(string="تصدير فقط العناصر ذات التكلفة", default=True)
    def open_export_wizard(self):
        self.ensure_one()
        return {
            'name': 'Export Components',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.cost.collector.export.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_collector_id': self.id}
        }

    @api.depends('total_cost_all')
    def _compute_total_cost_all_with_currency(self):
        for rec in self:
            if rec.total_cost_all:
                rec.total_cost_all_with_currency = f"{rec.total_cost_all:,.2f} EGP"
            else:
                rec.total_cost_all_with_currency = "0.00 EGP"
    #----------------------------------------------
    #----------------------------------------------

    @api.depends('component_line_ids.total_cost')
    def _compute_total_cost_all(self):
        for rec in self:
            rec.total_cost_all = sum(rec.component_line_ids.mapped('total_cost') or [])

    #    إنشاء رقم تسلسلي للطلب
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['date_time'] = Datetime.now()
        res = super().create(vals_list)
        for record in res:
            if record.ref == 'New':
                record.ref = self.env['ir.sequence'].next_by_code("cost_assembly_product_seq")
        return res

    # ✅ constrains: منع الحفظ نهائيًا لو البيانات غلط
    @api.constrains('finished_product_ids', 'global_qty')
    def _check_quantities_match(self):
        # لو الحقول دى فاضيه وقف المعالجه
        for rec in self:
            if not rec.finished_product_ids or not rec.global_qty:
                raise ValidationError("يجب إدخال الكميات و المنتجات وعدم تركه فارغة وان يكونوا متساويان!")
            # elif not rec.location_ids:
            #     raise ValidationError("يحب ادخال موقع المخزن وعدم تركه فارغا")
            # نحول من string الى list num مثلا من ("1-2-3") الي ["1","2","3"]
            quantities = [float(q.strip()) for q in rec.global_qty.split('-') if
                          q.strip().replace('.', '', 1).isdigit()]

            if len(quantities) != len(rec.finished_product_ids) != []:
                raise ValidationError("عدد الكميات يجب أن يساوي عدد المنتجات المحددة!")

    # =======================================================##############################################==================
    # =======================================================##############################################==================

    # =======================================================##############################################==================
    # =======================================================##############################################==================
    # دالة حساب المكونات
    @api.depends('finished_product_ids', 'location_ids', 'global_qty')
    @api.onchange('finished_product_ids', 'location_ids', 'global_qty')
    # -------------------------------------------------------------------
    def _onchange_products_quantities(self):
        self.ensure_one()
        try:
            self.component_line_ids = [(5, 0, 0)]  # مسح المكونات الحالية
            if not self.finished_product_ids or not self.global_qty:
                return

            if not isinstance(self.global_qty, str):
                raise ValidationError("حقل الكميات يجب ان يكون نصا مثل 1-2-3" "")

            quantities = [q.strip() for q in self.global_qty.split('-') if q.strip().isdigit()]
            product_qty_map = dict(zip(self.finished_product_ids, map(float, quantities)))
            component_dict = defaultdict(float)
            # ============= Start Calling Components =========================#
            # بنلف على كل منتج + كميته
            for product, qty in product_qty_map.items():
                bom = self.env['mrp.bom'].search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('active', '=', True)
                ], order='sequence, id', limit=1)
                if bom:
                    for bom_line in bom.bom_line_ids:
                        component_product = bom_line.product_id
                        component_qty = bom_line.product_qty * qty  # / qty_of_finished_product or 1
                        if bom_line.product_id:
                            component_dict[component_product] += component_qty
                        else:
                            component_dict[component_product] = component_qty

            # تحديث قائمة المكونات
            new_lines = []
            for product, qty in component_dict.items():
                # available_qty = self.env['stock.quant']._get_available_quantity(product,
                #                                                                 self.location_id) if self.location_id else 0
                available_qty = sum(
                    self.env['stock.quant']._get_available_quantity(product, location)
                    for location in self.location_ids) if self.location_ids else 0
                missing_qty = max(0, qty - available_qty)

                new_lines.append((0, 0, {
                    'product_id': product.id,
                    'required_qty': qty,
                    'available_qty': available_qty,
                    'missing_qty': missing_qty,
                    'product_uom_id': product.uom_id.id
                }))
            self.component_line_ids = new_lines
        except Exception as error:
            raise ValidationError(str(error))

    def compute_components(self):
        self._check_quantities_match()
        self._onchange_products_quantities()
    # ============= End Calling Components =========================#


# ============ start  classes showing Components in Lines  ===========================#
class AssembleOrderComponent(models.Model):
    _name = 'mrp.cost.collector.line'
    _description = 'cost collector line'
    # _order = 'sequence'
    # sequence = fields.Integer(string="Sequence", dafault=20)

    order_id = fields.Many2one('mrp.cost.collector', string='Kit Assembly Order')
    product_id = fields.Many2one('product.product', string='component', required=True)
    required_qty = fields.Float(string='Required Qty', digits='Product Unit of Measure', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='Unit Of Measure')
    available_qty = fields.Float(string='Available in Sub-Inventory')
    missing_qty = fields.Float(string='Missing Quantity')

    purchase_cost = fields.Float(string='Unit Cost', compute="_compute_purchase_cost", store=True)

    total_cost = fields.Float(string='Total Cost', compute="_compute_total_cost", store=True)

    @api.depends('product_id')
    def _compute_purchase_cost(self):
        for line in self:
            line.purchase_cost = line.product_id.standard_price or 0.0

    total_cost_with_currency = fields.Char(
        string='Total Cost',
        compute='_compute_purchase_cost_with_currency',
        store=True,
    )
    @api.depends('required_qty', 'purchase_cost','total_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.missing_qty * line.purchase_cost
            if line.total_cost:
                line.total_cost_with_currency = f"{line.total_cost:.2f} EGP"
            else:
                line.total_cost_with_currency = "0.00 EGP"



    purchase_cost_with_currency = fields.Char(
        string='Unit Cost',
        compute='_compute_purchase_cost_with_currency',
        store=True,
    )

    @api.depends('purchase_cost')
    def _compute_purchase_cost_with_currency(self):
        for rec in self:
            if rec.purchase_cost:
                rec.purchase_cost_with_currency = f"{rec.purchase_cost:,.2f} EGP"
            else:
                rec.purchase_cost_with_currency = "0.00 EGP"