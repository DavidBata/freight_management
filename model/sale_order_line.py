from werkzeug import urls
from odoo import api, fields, models, _

import datetime
class OrderLineFreight(models.Model):
    _inherit = "sale.order.line"
    _description = "Agg, fields freight_order"

    freight_order = fields.Boolean("Freight Order", default=False)
    freight_order_id = fields.Many2one(
        "freight.order", string="freight_order", default=False, store=True
    )
    product_weight = fields.Float(
        string="Peso de Producto", related="product_id.weight"
    )
    
    fecha_vencimiento = fields.Date(
        string='Fecha Vencimiento',
        compute="_compute_fecha_vencimiento",
        store=True,
        # default=fields.Date.context_today,
    )
    
    hoy = fields.Date(
        string='hoy',
        # default=fields.Date.context_today,
        compute="_compute_hoy"
    )
    
    
    order_id_caleta = fields.Selection(
        string="caleta", related="order_id.caleta", store=True
    )
    
    validity_date = fields.Date(
        string='Fecha Prometida',
        related='order_id.validity_date'
    )
    
    order_id_mota_carga = fields.Selection(
        string="Mota Carga", store=True, related="order_id.mota_carga"
    )

    delivery_address_id = fields.Many2one(
        related="order_id.delivery_address_id", store=True, string="Direc Entrega"
    )

    price_unit_limite = fields.Float(
        string="Precio Limite", related="product_template_id.list_price_limit"
    )
    list_price_limit = fields.Float(
        string="Precio Limite", related="product_template_id.list_price_limit"
    )
    list_price = fields.Float(
        string="Precio Unit", related="product_template_id.list_price"
    )
    destination_company_id = fields.Many2one(
        related="product_template_id.destination_company_id",
        store=True,
        string="Compañia de Destino",
    )
    vat = fields.Char(related="order_partner_id.vat", string="RIF")
    type_negociate_id = fields.Many2one(
        related="order_id.pricelist_id", string="Tipo de Negociacion", store=True
    )
    list_price_partner = fields.Many2one(
        related="order_partner_id.property_product_pricelist",
        string="Canal Venta",
    )
    canal_sale = fields.Char(
        string="Tipo de Canal",
        related="order_id.canal_sale",
        store=True,
        readonly=True,
    )
    date_order = fields.Date(
        related="freight_order_id.date_upload", string=" Fecha de Carga", default=False
    )
    costo_unit = fields.Float(
        related="product_template_id.standard_price", store=True, string="precion Unitario"
    )
    document_type = fields.Char(related='order_id.name_document', store=True)
    
     
    is_opl = fields.Boolean(
        string='Cliente Opl(Adempiere)',
        related='order_partner_id.is_opl'
    )
    
    state_line = fields.Selection(
        string='state_back',
        selection=[('back_order', 'Orden Regresada'), ('complete', 'Completado')]
    )
    back_order_id = fields.Many2one(
        string='Back Order',
        comodel_name='back.order',
        ondelete='restrict',
    )
    
    
    def create_order_freicht(self):
        return {
            "name": _("Orden Carga"),
            "res_model": "freight.order",
            "view_mode": "form",
            "target": "new",
            "type": "ir.actions.act_window",
            "context": {"default_sale_order_line_ids": self.ids},
        }
    

    @api.depends('create_date')
    def _compute_fecha_vencimiento(self):
        for rec in self:
            fecha_prometida = rec.create_date
            fecha_vencimento = fecha_prometida + datetime.timedelta(weeks=2)
            rec.fecha_vencimiento = fecha_vencimento
    def crear_back_order(self):
        for rec in self:
            if rec.freight_order:
                raise ValueError("Una o Mas lineas Petenece a una Orden de Carga")
    
        return {
        "name": _("Back Order"),
        "res_model": "back.order",
        "view_mode": "form",
        "target": "new",
        "type": "ir.actions.act_window",
        "context": {"default_sale_order_line_ids": self.ids},
        }
            
    
    
    