
from werkzeug import urls
from odoo import api, fields, models, _


class FleetVehicleFreight(models.Model):
    _inherit = 'fleet.vehicle'

    ability = fields.Float(
        string="Capacidad", help="Capacidad en KG del Vehiculo")
