# -*- coding: utf-8 -*-

from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightOrder(models.Model):

    _inherit = 'product.template'
    _description = 'agg Campo de Limite de precio'

    list_price_limit = fields.Float(string="Precio Limite de Venta")

    destination_company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Compañia de Destino',
    )
