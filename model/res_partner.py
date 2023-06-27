from werkzeug import urls
import requests
import xml.etree.ElementTree as El
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class ResPartnerAggSaleOrder(models.Model):
    _inherit = "res.partner"

    canal_sale = fields.Char(
        string="Tipo de Canal", compute="_compute_canal_sale", readonly=True
    )
    
    responsable_id = fields.Many2one(
        'res.users',
        string='responsable',
    )
    
    is_opl = fields.Boolean(
        string='Cliente Opl(Adempiere)', 
        default=False
    )
    
    
    
    
    @api.depends("vat")
    def _compute_canal_sale(self):
        for rec in self:
            
            try:
                url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"
                vat = rec.vat
                payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>CanalSales</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"TaxID\">\r\n                        <_0:val>{vat}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
                headers = {"Content-Type": "application/xml"}
                response = requests.request("POST", url, headers=headers, data=payload)
                xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
                canal_id = rec.env["web.service.eng"].get_data_response(xml=xml)
                if canal_id:
                    id = canal_id[0]
                else:
                    id = ""
                canal = rec.canal_venta(c_chanel=id)
                rec.canal_sale = canal
                
            except :
                rec.canal_sale=" "
                
    def canal_venta(self, c_chanel):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>NombreCanalVenta</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"C_Channel_ID\">\r\n                        <_0:val>{c_chanel}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)
        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        canal = self.env["web.service.eng"].get_data_response(xml=xml)

        return canal
