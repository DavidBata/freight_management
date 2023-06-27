import requests
import xml.etree.ElementTree as El
import tempfile
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# READONLY_FIELD_STATES = {state: [("readonly", True)] for state in {"import_ademp"}}
class BackOrder(models.Model):
    _name = "back.order"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "back order"
    name = fields.Char(
        string='Nombre',
    )
    description = fields.Text(
        string='Description',
    )
    sale_order_line_ids = fields.One2many(
        string='Lineas Back Order',
        comodel_name='sale.order.line',
        inverse_name='back_order_id',
        readonly=True
    )
    retraso = fields.Boolean(
        string='Restraso',
    )
    
    motivo_bo = fields.Selection(
        string='Motivo Back Order',
        selection=[
        ('BO-10', 'QUIEBRE DE STOCK POR MATERIA PRIMA y MATERIAL DE EMPAQUE'), 
        ('BO-20', 'NO DISPONIBLE Al MOMENTO DEL DESPACHO'),
        ('BO-30', 'NO ACTIVO EN CUOTA'),
        ('BO-50', 'GENERADO POR QUIEBRE DE INVENTARIO DE OTRA CATEGORIA'),
        ('ELI-10', 'ELIMINAR PEDIDO A PETICION DEL EQUIPO DE VENTA'),
        ])
    motivo_retraso = fields.Selection(
        string='Motivo Retraso',
        selection=[
        ('PTA-10', 'DISPONIBILIDAD DE PRODUCTO (CAUSA)'),
        ('PTA-11', 'RETRASO ATRIBUIDO A PRODUCTO (CAUSA)'),
        ('PTA-20', 'DISPONIBILIDAD DE VEHICULO '),
        ('VEN-10', 'CONSOLIDACION DE CARGA '),
        ('VEN-20', 'RECEPCIÓN DE PEDIDO FUERA DE HORARIO'),
        ('VEN-30', 'FECHA ESTIMADA DE DESPACHO MENOR A 48 HORAS '),
        ('VEN-40', 'PHASING DE VENTA MAYOR CAPACIDAD DE PRODUCCIÓN '),
        ('PLA-10', 'OMISIÓN DE SOLICITUDES DE DESPACHO '),
        ('APR-10', 'APROBACIONES POR DIRECCION COMERCIAL '),
        ('APR-20', 'APROBACIONES O GERENTES REGIONALES '),
        ('VEN-50', 'SOLICITUDES CON ERRORES EN LOS PARAMETROS DE FACTURACIÓN '),
        ('OTR-10', 'OTROS')
        ])



    field_name = fields.Selection(
        string='field_name',
        selection=[('valor1', 'valor1'), ('valor2', 'valor2')]
    )
    
    
    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = "back.order.sequence"
        sequence_code_retraso = "back.order.sequence.retraso"
        if vals["retraso"]==True:
            vals["name"] = self.env["ir.sequence"].next_by_code(sequence_code_retraso)
            return super(BackOrder, self).create(vals)
        else: 
            vals["name"] = self.env["ir.sequence"].next_by_code(sequence_code)
            return super(BackOrder, self).create(vals)

    @api.onchange('retraso')
    def _onchange_retraso(self):
        for rec in self:
            if  rec.retraso == False:
                rec.motivo_retraso = False
            else:
                rec.motivo_bo = False
        pass