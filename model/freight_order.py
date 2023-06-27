# -*- coding: utf-8 -*-

import requests

# from xml.etree.ElementTree import parse, Element
import xml.etree.ElementTree as El
import tempfile
# import pandas as pd
# from werkzeug import urls
# from xml.dom import minidom
# import WebServiceEng

import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

READONLY_FIELD_STATES = {state: [("readonly", True)] for state in {"import_ademp"}}


class FreightOrder(models.Model):
    _name = "freight.order"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Freight Order"

    name = fields.Char("Name", default="Nuevo", readonly=True)

    truck_id = fields.Many2one(
        "fleet.vehicle",
        "Vehiculo",
        required=True,
        tracking=1,
        states=READONLY_FIELD_STATES,
    )

    sale_order_id = fields.Many2one(
        "sale.order", string="Pedido", tracking=1, states=READONLY_FIELD_STATES
    )

    # sale_order_ids = fields.One2many('sale.order.line', 'freight_order_id')

    date_upload = fields.Date(
        string="Fecha de Carga",
        default=fields.Date.today(),
        tracking=1,
        states=READONLY_FIELD_STATES,
    )

    order_date = fields.Date(
        "Fecha de Orden",
        default=fields.Date.today(),
        help="Date of order",
        tracking=1,
        states=READONLY_FIELD_STATES,
    )

    sale_order_line_ids = fields.Many2many(
        "sale.order.line",
        domain="[('freight_order', '=', False),('state', '=', 'sale')]",
        string="Order Lines",
        tracking=1,
        states=READONLY_FIELD_STATES,
    )
    
    tipo_document_opl = fields.Selection(
        string='Tipo/Documento Orden Distribuciion',
        selection=
        [('Orden de Distribución (TI)', 'Orden de Distribución (TI)'), 
        ('Orden de Distribución (MS)', 'Orden de Distribución (MS)'),
        ('Orden de Distribución (MI)','Orden de Distribución (MI)'),
        ('Orden de Distribución (AC)','Orden de Distribución (AC)'
        )]
    )

    



    is_opl = fields.Boolean(
        string='Clinete Opl(Adempiere)',
        default=False,
        compute="_compute_cliente_opl"
    )
    
    
    state = fields.Selection(
        [("draft", "Borrador"), ("sent", "Confirmado"), ("import_ademp", "Importado")],
        tracking=1,
        default="draft",
    )

    accumulator_weight = fields.Float(
        string="Peso Acumulado",
        compute="_compute_linea_peso",
        states=READONLY_FIELD_STATES,
    )

    truck_weight = fields.Float(
        string="Capacidad de Vehiculo",
        related="truck_id.ability",
        states=READONLY_FIELD_STATES,
    )

    driver_id = fields.Many2one(
        related="truck_id.driver_id",
        string="driver",
        store=True,
        readonly=False,
        states=READONLY_FIELD_STATES,
    )
    crear_c_order_in_id = fields.Many2one(
        "web.service.eng",
        string="Destino de Adempiere",
        states=READONLY_FIELD_STATES
    )
    user_id = fields.Many2one(
        "res.users",
        string="Usuario",
        tracking=1,
        compute="_compute_user_id",
        store=True,
        states=READONLY_FIELD_STATES,
    )
    @api.depends('sale_order_line_ids')
    def _compute_cliente_opl(self):
        for rec in self: 
            is_true=[]
            is_false = []
            for line in rec.sale_order_line_ids:
                if line.order_partner_id.parent_id.is_opl:
                    is_true.append(line.order_partner_id.parent_id.is_opl)
                else: 
                    is_false.append(line.order_partner_id.parent_id.is_opl)
                
            if len(rec.sale_order_line_ids) == len(is_true) and len(is_false)==0 and len(rec.sale_order_line_ids)>0:               
                rec.is_opl= True
            else: 
                rec.is_opl= False
        # raise  ValidationError(sum(is_true))
    @api.model
    def create(self, vals):
        """Create Sequence"""
        sequence_code = "freight.order.sequence"
        vals["name"] = self.env["ir.sequence"].next_by_code(sequence_code)
        return super(FreightOrder, self).create(vals)

    @api.constrains("truck_id", "sale_order_line_ids")
    def _check_sale_order_lien_cargada(self):
        for rec in self:
            for x in rec.sale_order_line_ids:
                if x.freight_order == True:
                    raise ValidationError(
                        _("Una o mas Lineas de Venta Ya Tienen Orden de Carga")
                    )

            if rec.truck_id and rec.accumulator_weight <= rec.truck_weight:
                rec.state = "draft"
            else:
                raise ValidationError(
                    _("Peso Total, Supera a la Capacidad Del Transporte")
                )
    # def create_order_distribucion(self):
        
    def confirmar_freight(self):
        freight_order = self.env["freight.order"].search(
            [("sale_order_line_ids", "!=", " ")]
        )
        # breakpoint()
        for rec in self:
            if rec.sale_order_line_ids and rec.sale_order_line_ids.order_id:
                for s in rec.sale_order_line_ids:
                    s.freight_order = True

                    s.freight_order_id = rec.id
                rec.state = "sent"
            else:
                self.state = "draft"
                raise ValidationError(
                    _(
                        "Debe tener Lineas de Pedido el Camion o uno de los pedidos ya se agrego"
                    )
                )

    def import_pedido(self):
        for rec in self:
            lista = []
            for line in rec.sale_order_line_ids:
                cont_line = line.destination_company_id
                if cont_line not in lista:
                    lista.append(line.destination_company_id)
            if len(lista) > 1:
                raise ValidationError("Las no tienen la misma compañia de destino")

    @api.depends("sale_order_line_ids")
    def _compute_linea_peso(self):
        for rec in self:
            rec.accumulator_weight = 0
            if rec.sale_order_line_ids:
                weight = []
                for i in rec.sale_order_line_ids:
                    weight.append(i.product_weight * i.product_uom_qty)
                rec.accumulator_weight = sum(weight)

    @api.depends("truck_id")
    def _compute_user_id(self):
        for rec in self:
            if not rec.user_id:
                rec.user_id = self.env.user
    def tipo_documeto_order_distribucion(self,name):
        for rec in self:

            url=rec.crear_c_order_in_id.url
            payload = f"""
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:queryData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>TypeDocumentOrderVenta</adin:serviceType>
                            <!--Optional:-->
                            <adin:DataRow>
                                <adin:field column="Name">
                                    <adin:val>{name}</adin:val>
                                </adin:field>
                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>dGarcia</adin:user>
                            <adin:pass>dGarcia</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>1000000</adin:ClientID>
                            <adin:RoleID>1000000</adin:RoleID>
                            <adin:OrgID>0</adin:OrgID>
                            <adin:WarehouseID>0</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                    </adin:createData>
                </soapenv:Body>
            </soapenv:Envelope>"""
            headers = {"Content-Type": "application/xml"}

            response = requests.request("POST", url, headers=headers, data=payload)

            xml_unific = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
            lista_data = self.get_data_response(xml=xml_unific)
            # raise ValidationError(response.text)
            return lista_data
    def import_orden_distribucion(self):
        for rec in self:
            
            # raise ValidationError(rec)
            rifs = []
            record = []
            for line in rec.sale_order_line_ids:
                if line.vat not in rifs:
                    admpiere_partner_id = rec.crear_c_order_in_id.consul_cb_partner(CI=line.vat, url=rec.crear_c_order_in_id.url)
                    # raise ValidationError(admpiere_partner_id["partner"])
                    partnet_adem = admpiere_partner_id["partner"]
                    user_admpiere = rec.crear_c_order_in_id.consul_user(code=rec.env.user.login,url=rec.crear_c_order_in_id.url)
                    # raise ValidationError(user_admpiere["rol_id"] )
                    # LOGUE DE USUARIO CREDENCIALES
                    user = user_admpiere["value"]
                    clave = user_admpiere["value"]
                    client_id = "1000000"
                    role_id = user_admpiere["rol_id"]
                    org_id = user_admpiere["ad_org_id"]
                    WarehouseID = user_admpiere["almacen"]
                    consulta_documento=rec.tipo_documeto_order_distribucion(name=rec.tipo_document_opl)
                    DocTypeTarget= consulta_documento[0]
                    
                    # direcion_entrega = self.direccion_entrega(cb_partner_id=partnet_adem,name_direccion=line.order_partner_id.city.upper(),url=rec.crear_c_order_in_id.url)
                      
                    # raise ValidationError(WarehouseID)  
                    # LOGUE DE USUARIO CREDENCIALES
                    # Crando LA ORDEN DE VENTA EN ADEMPIERE
                    ad_client = "1000000"
            
                    c_order_admpiere = rec.crear_c_order_in_id.dd_order_create(
                        user=user,
                        clave=clave,
                        ClientID=client_id,
                        RoleID=role_id,
                        OrgID=org_id,
                        WarehouseID=WarehouseID,
                        C_BPartner_ID=partnet_adem,
                        M_Warehouse_ID=WarehouseID,
                        Description=rec.name +' '+ "Import Ws",
                        C_DocTypeTarget_ID=DocTypeTarget,
                        AD_Client_ID=ad_client,
                        url=rec.crear_c_order_in_id.url,
                    )
                    record += c_order_admpiere
                    rifs.append(line.vat)
            # raise ValidationError(c_order_admpiere)
            register = dict(zip(rifs, record))
            register_comp = dict(zip(record, rifs))
            
            # raise ValidationError(register.items())
            create_order_line = rec.create_order_line_distribucion(
                order_id=register,
                clave=clave,
                user=user,
                ClientID=client_id,
                RoleID=role_id,
                OrgID=org_id,
                WarehouseID=WarehouseID,
                url=rec.crear_c_order_in_id.url,
            )
            # raise ValidationError(create_order_line)
            
            for respon in create_order_line:
                reco_id = rec.get_data_response(xml=respon)
                is_int = int(reco_id[0])
                if type(is_int) is int:
                    succ = True
                else:
                    succ = False
            if succ:
                rec.state = "import_ademp"

                # raise ValidationError(_("Exito, En Creacion de Ordenes de Venta"))
            else:
                raise ValidationError(
                    _("Comunicate con el Administrador, Algo Salio Mal")
                )
        if  len(rec)>=1:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "message": _("Las Ordenes Fueron Creadas."),
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
    def import_adempiere(self):
        for rec in self:
            # raise ValidationError(rec)
            rifs = []
            record = []
            for line in rec.sale_order_line_ids:
                if line.vat not in rifs:
                    admpiere_partner_id = rec.crear_c_order_in_id.consul_cb_partner(CI=line.vat, url=rec.crear_c_order_in_id.url)
                    
                    # raise ValidationError(admpiere_partner_id["partner"])
                    partnet_adem = admpiere_partner_id["partner"]
                    user_admpiere = rec.crear_c_order_in_id.consul_user(code=rec.env.user.login,url=rec.crear_c_order_in_id.url)
                    
                    # raise ValidationError(user_admpiere["rol_id"] )
                    # LOGUE DE USUARIO CREDENCIALES
                    user = user_admpiere["value"]
                    clave = user_admpiere["value"]
                    client_id = "1000000"
                    role_id = user_admpiere["rol_id"]
                    org_id = user_admpiere["ad_org_id"]
                    WarehouseID = user_admpiere["almacen"]
                    DocTypeTarget= line.document_type
                    direcion_entrega = self.direccion_entrega(cb_partner_id=partnet_adem,name_direccion=line.order_partner_id.city.upper(),url=rec.crear_c_order_in_id.url)
                      
                    # raise ValidationError(WarehouseID)  
                    # LOGUE DE USUARIO CREDENCIALES
                    # Crando LA ORDEN DE VENTA EN ADEMPIERE
                    ad_client = "1000000"
            
                    c_order_admpiere = rec.crear_c_order_in_id.web_service_c_order(
                        user=user,
                        clave=clave,
                        ClientID=client_id,
                        RoleID=role_id,
                        OrgID=org_id,
                        WarehouseID=WarehouseID,
                        C_BPartner_ID=partnet_adem,
                        C_Campaign_ID="1000000",
                        C_Project_ID="1000018",
                        M_Warehouse_ID=WarehouseID,
                        Description=rec.name +' '+ "Import_Ws ",
                    
                        C_DocTypeTarget_ID=DocTypeTarget,
                        AD_Client_ID=ad_client,
                        url=rec.crear_c_order_in_id.url,
                    )
                    # raise ValidationError(c_order_admpiere)  
                    
                    actulizacio=self.update_direccion_entrega(order_id=c_order_admpiere[0],C_BPartner_Location_ID=direcion_entrega,url=rec.crear_c_order_in_id.url)

                    
                    record += c_order_admpiere
                    rifs.append(line.vat)
            
            register = dict(zip(rifs, record))
            register_comp = dict(zip(record, rifs))
            
            # raise ValidationError(register.items())
            create_order_line = rec.create_order_line(
                order_id=register,
                clave=clave,
                user=user,
                ClientID=client_id,
                RoleID=role_id,
                OrgID=org_id,
                WarehouseID=WarehouseID,
                url=rec.crear_c_order_in_id.url,
            )

            
            for respon in create_order_line:
                reco_id = rec.get_data_response(xml=respon)
                is_int = int(reco_id[0])
                if type(is_int) is int:
                    succ = True
                else:
                    succ = False
            if succ:
                rec.state = "import_ademp"

                # raise ValidationError(_("Exito, En Creacion de Ordenes de Venta"))
            else:
                raise ValidationError(
                    _("Comunicate con el Administrador, Algo Salio Mal")
                )
        if  len(rec)>=1:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "message": _("Las Ordenes Fueron Creadas."),
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        # if lista_produdctos_registrados:
        #     ids_order_line = []
        #     for id_register in lista_produdctos_registrados:
        #         id_order_line = rec.get_data_response(xml=id_register)
        #         ids_order_line.append(id_order_line)
        #     if ids_order_line:
        #         rec.state = "import_ademp"

        # else:
        #     raise ValidationError("No hay vida")

        # def create_c_order_adm(self):
        # for sku in rec.sale_order_line_ids:
        #     dic[cont] = sku
        #     cont += 1

        #     web_service = self.env['web.service.eng'].search([])
        #     company = self.env.company
        #     sin = web_service.conection_url_admpiere(2)
        #     raise ValidationError(sin)
    
    def notification(self):
        msg = _("Exito, Orden de Venta Creda")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "success",
                "message": msg,
                "sticky": True,
            },
        }

    def web_service_c_order(
        self,
        user,
        clave,
        ClientID,
        RoleID,
        OrgID,
        WarehouseID,
        AD_Client_ID,
        C_DocTypeTarget_ID,
        Description,
        C_BPartner_ID,
        C_Campaign_ID,
        C_Project_ID,
        M_Warehouse_ID,
    ):
        url = "http://adempiere-qa-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
        <soapenv:Header/>
        <soapenv:Body>
            <adin:createData>
                <adin:ModelCRUDRequest>
                    <adin:ModelCRUD>
                    <adin:serviceType>CreateOrderPedidos</adin:serviceType>
                    <adin:TableName>C_Order</adin:TableName>
                    <adin:RecordID>0</adin:RecordID>

                    <adin:Action>Create</adin:Action>
                    <adin:PageNo>0</adin:PageNo>
                    <!--Optional:-->
                    <adin:DataRow>

                        <adin:field column="AD_Client_ID">
                            <adin:val>{AD_Client_ID}</adin:val>
                        </adin:field>
                        <adin:field column="AD_Org_ID">
                            <adin:val>{OrgID}</adin:val>
                        </adin:field>
                        <adin:field column="C_DocTypeTarget_ID">
                            <adin:val>{C_DocTypeTarget_ID}</adin:val>
                        </adin:field>
                        <adin:field column="Description">
                            <adin:val>{Description}</adin:val>
                        </adin:field>

                        <adin:field column="C_BPartner_ID">
                            <adin:val>{C_BPartner_ID}</adin:val>
                        </adin:field>

                        <adin:field column="C_Campaign_ID">
                            <adin:val>{C_Campaign_ID}</adin:val>
                        </adin:field>
                        <adin:field column="C_Project_ID">
                            <adin:val>{C_Project_ID}</adin:val>
                        </adin:field>
                        <adin:field column="M_Warehouse_ID">
                            <adin:val>{M_Warehouse_ID}</adin:val>
                        </adin:field>

                    </adin:DataRow>
                    </adin:ModelCRUD>
                    <adin:ADLoginRequest>
                    <adin:user>{user}</adin:user>
                    <adin:pass>{user}</adin:pass>
                    <adin:lang>es_VE</adin:lang>
                    <adin:ClientID>{ClientID}</adin:ClientID>
                    <adin:RoleID>{RoleID}</adin:RoleID>
                    <adin:OrgID>{OrgID}</adin:OrgID>
                    <adin:WarehouseID>{M_Warehouse_ID}</adin:WarehouseID>
                    <adin:stage>0</adin:stage>
                    </adin:ADLoginRequest>
                </adin:ModelCRUDRequest>
            </adin:createData>
        </soapenv:Body>
        </soapenv:Envelope>

        """
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml_unific = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        lista_data = self.get_data_response(xml=xml_unific)
        # raise ValidationError(response.text)
        return lista_data

    def get_data_response(self, xml):
        doc_xml = El.fromstring(xml)
        doc_xml.items()
        data_resp = []
        lista = []
        for x in doc_xml.iter():
            # print(x.attrib)
            if x.attrib and len(x.attrib) <= 2:
                data_resp.append(x.attrib)
            cont = 0
        for part in data_resp:
            for cont, value in part.items():
                dic = {
                    cont: value,
                }

            for valida in dic.values():
                lista.append(valida)
        # raise ValidationError(valida)
        return lista


    def consul_cb_partner(self, CI):
        url = "http://adempiere-engine.iancarina.com.ve//ADInterface/services/ModelADService"

        payload = f"""<?xml version='1.0' encoding='UTF-8'?> <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>CBPartnerConsul</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"TaxID\">\r\n                        <_0:val>{CI}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}
        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

        doc_xml = El.fromstring(xml)
        doc_xml.items()
        # print(doc_xml.iter())
        data_cbpart = []
        dic = {}
        cont = 0
        for x in doc_xml.iter():
            # print(x.attrib)
            if x.attrib and len(x.attrib) <= 2:
                data_cbpart.append(x.attrib)
            cont = 0
            lista = []
        for part in data_cbpart:
            for cont, value in part.items():
                dic = {
                    cont: value,
                }

            for valida in dic.values():
                lista.append(valida)
        # lista.sort()
        # raise ValidationError(lista)
        diccio = {
            "partner": lista[0],
        }
        return diccio

    def consul_user(self, code):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConsulUsuario</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"Value\">\r\n                        <_0:val>{code}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

        doc_xml = El.fromstring(xml)
        doc_xml.items()
        print(doc_xml.items)
        data_cbpart = []
        dic = {}
        cont = 0
        for x in doc_xml.iter():
            # print(x.attrib)
            if x.attrib and len(x.attrib) <= 2:
                data_cbpart.append(x.attrib)
            cont = 0
            lista = []
        for part in data_cbpart:
            for cont, value in part.items():
                dic = {
                    cont: value,
                }
            for valida in dic.values():
                lista.append(valida)

        lista.sort()
        # raise ValidationError(lista)
        consul_org = self.consul_organiz_user_acc(org_acc=lista[2])
        consul_rol = self.consul_rol_user(user_id=lista[2])
        org_asignado = consul_org[0]
        consul_alma = self.consul_almacen_user(org_id=org_asignado)

        # raise ValidationError(consul_tipodc)
        # print(lista)
        diccio = {
            "almacen": consul_alma[0],
            "rol_id": consul_rol[0],
            "ad_org_id": org_asignado,
            "org_tans": lista[1],
            "user_id": lista[2],
            "password": lista[3],
            "name": lista[4],
            "value": lista[5],
        }

        return diccio

    def consul_organiz_user_acc(self, org_acc):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConusultOrganizAcceso</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"AD_User_ID\">\r\n                        <_0:val>{org_acc}</_0:val>\r\n            </_0:field>\r\n <_0:field column=\"IsActive\">\r\n                        <_0:val>Y</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

        doc_xml = El.fromstring(xml)
        doc_xml.items()
        # print(doc_xml.iter)
        data_cbpart = []
        dic = {}
        cont = 0
        for x in doc_xml.iter():
            # print(x.attrib)
            if x.attrib and len(x.attrib) <= 2:
                data_cbpart.append(x.attrib)
            cont = 0
            lista = []
        for part in data_cbpart:
            for cont, value in part.items():
                dic = {
                    cont: value,
                }

            for valida in dic.values():
                lista.append(valida)

        return lista

    def consul_rol_user(self, user_id):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>RoleUserAccs</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"AD_User_ID\">\r\n                        <_0:val>{user_id}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        rol_user = self.get_data_response(xml=xml)
        return rol_user

    def consul_almacen_user(self, org_id):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>AlmacenIDAcssLog</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"AD_Org_ID\">\r\n                        <_0:val>{org_id}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        almacen_id = self.get_data_response(xml=xml)
        return almacen_id

    def consul_documet_type(self, org_id):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>TypeDocumentOrderVenta</_0:serviceType>\r\n          <_0:DataRow>\r\n <_0:field column=\"AD_Org_ID\">\r\n                        <_0:val>{org_id}</_0:val>\r\n            </_0:field>\r\n <_0:field column=\"IsSOTrx\">\r\n                        <_0:val>Y</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        document_type = self.get_data_response(xml=xml)
        ids = []
        names = []
        dic = {}

        for doc in document_type:
            try:
                i = int(doc)
                if type(i) is int:
                    ids.append(doc)
            except ValueError:
                names.append(doc)
        dic = dict(zip(names, ids))

        return dic
    def direccion_entrega(self, cb_partner_id, name_direccion,url):
        for rec in self:
            # url= rec.crear_c_order_in_id.url
            
            payload = f"""
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:queryData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>DireccionEntregaLocationPartner</adin:serviceType>
                        
                            <!--Optional:-->
                            <adin:DataRow>

                                <adin:field column="Name">
                                    <adin:val>{name_direccion}</adin:val>
                                </adin:field>
                                <adin:field column="C_BPartner_ID">
                                    <adin:val>{cb_partner_id}</adin:val>
                                </adin:field>
                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>dGarcia</adin:user>
                            <adin:pass>dGarcia</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>1000000</adin:ClientID>
                            <adin:RoleID>1000000</adin:RoleID>
                            <adin:OrgID>0</adin:OrgID>
                            <adin:WarehouseID>0</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                    </adin:createData>
                </soapenv:Body>
            </soapenv:Envelope>
            """
            headers = {"Content-Type": "application/xml"}
            response = requests.request("POST", url, headers=headers, data=payload)
            xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
            # raise ValidationError(response.text)
            id_direction_entrega = self.get_data_response(xml=xml)
            # raise ValidationError(id_direction_entrega)
            return id_direction_entrega[0]
    
    def create_order_line(
        self, order_id, user, clave, ClientID, RoleID, OrgID, WarehouseID, url
    ):
        lista_produdctos_registrados = []
        lista_code_pr = []
        for rec in self:
            strin = " - "
            for code_product in rec.sale_order_line_ids:
                codigo_producto = code_product.product_template_id.name
                indice = codigo_producto.find(strin)
                # lista_code_pr.append(codigo_producto[:indice])
                producto_ad_id = rec.consul_id_product(
                    code=codigo_producto[:indice], url=rec.crear_c_order_in_id.url
                )
                QtyEntered=code_product.product_uom_qty
                PriceActual=code_product.price_unit
                c_order_id = order_id[code_product.vat]
                PriceEntered= code_product.price_unit
                # raise ValidationError(order_id[code_product.vat])
                payload = f"""
                 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:createData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>CreateOrderLinePedidos</adin:serviceType>
                            <!-- <adin:TableName>C_Order</adin:TableName> -->
                            <adin:RecordID>0</adin:RecordID>
                            <!-- <adin:Action>Create</adin:Action> -->
                            <adin:PageNo>0</adin:PageNo>
                            <!--Optional:-->
                            <adin:DataRow>
                                <adin:field column="C_Order_ID">
                                    <adin:val>{c_order_id}</adin:val>
                                </adin:field>
                                <adin:field column="M_Product_ID">
                                    <adin:val>{producto_ad_id}</adin:val>
                                </adin:field>

                                <adin:field column="QtyEntered">
                                    <adin:val>{QtyEntered}</adin:val>
                                </adin:field>
                                <adin:field column="PriceEntered">
                                    <adin:val>{PriceEntered}</adin:val>
                                </adin:field>
                                <adin:field column="PriceActual">
                                    <adin:val>{PriceActual}</adin:val>
                                </adin:field>

                                <adin:field column="AD_OrgTrx_ID">
                                    <adin:val>{OrgID}</adin:val>
                                </adin:field>

                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>{user}</adin:user>
                            <adin:pass>{user}</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>{ClientID}</adin:ClientID>
                            <adin:RoleID>{RoleID}</adin:RoleID>
                            <adin:OrgID>{OrgID}</adin:OrgID>
                            <adin:WarehouseID>{WarehouseID}</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                        </adin:queryData>
                    </soapenv:Body>
                    </soapenv:Envelope>

                """
                headers = {"Content-Type": "application/xml"}

                response = requests.request("POST", url, headers=headers, data=payload)

                lista_produdctos_registrados.append(response.text)
            # raise ValidationError(response.text)
            return lista_produdctos_registrados
    def create_order_line_distribucion(
        self, order_id, user, clave, ClientID, RoleID, OrgID, WarehouseID, url
    ):
        lista_produdctos_registrados = []
        lista_code_pr = []
        for rec in self:
            strin = " - "
            for code_product in rec.sale_order_line_ids:
                codigo_producto = code_product.product_template_id.name
                indice = codigo_producto.find(strin)
                # lista_code_pr.append(codigo_producto[:indice])
                producto_ad_id = rec.consul_id_product(
                    code=codigo_producto[:indice], url=rec.crear_c_order_in_id.url
                )
                fecha_hoy= datetime.datetime.today() 
                fecha_prometida= fecha_hoy + datetime.timedelta(days=2)
                # raise ValidationError(fecha_prometida)
                QtyEntered=code_product.product_uom_qty
                PriceActual=code_product.price_unit
                c_order_id = order_id[code_product.vat]
                PriceEntered= code_product.price_unit
                # raise ValidationError(order_id[code_product.vat])
                payload = f"""
                 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:createData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>OrderDistribucionLine</adin:serviceType>
                            <!-- <adin:TableName>C_Order</adin:TableName> -->
                            <adin:RecordID>0</adin:RecordID>
                            <!-- <adin:Action>Create</adin:Action> -->
                            <adin:PageNo>0</adin:PageNo>
                            <!--Optional:-->
                            <adin:DataRow>
                                <adin:field column="DD_Order_ID">
                                    <adin:val>{c_order_id}</adin:val>
                                </adin:field>
                                <adin:field column="M_Product_ID">
                                    <adin:val>{producto_ad_id}</adin:val>
                                </adin:field>

                                <adin:field column="QtyEntered">
                                    <adin:val>{QtyEntered}</adin:val>
                                </adin:field>

                                <adin:field column="M_LocatorTo_ID">
                                    <adin:val>1000155</adin:val>
                                </adin:field>

                                <adin:field column="M_Locator_ID">
                                    <adin:val>1000155</adin:val>
                                </adin:field>
                                 
                                <adin:field column="DateOrdered">
                                    <adin:val>{fecha_hoy}</adin:val>
                                </adin:field>
                                <adin:field column="DatePromised">
                                    <adin:val>{fecha_prometida}</adin:val>
                                </adin:field>
                                
                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>{user}</adin:user>
                            <adin:pass>{user}</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>{ClientID}</adin:ClientID>
                            <adin:RoleID>{RoleID}</adin:RoleID>
                            <adin:OrgID>{OrgID}</adin:OrgID>
                            <adin:WarehouseID>{WarehouseID}</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                        </adin:queryData>
                    </soapenv:Body>
                    </soapenv:Envelope>

                """
                headers = {"Content-Type": "application/xml"}
                
                response = requests.request("POST", url, headers=headers, data=payload)

                lista_produdctos_registrados.append(response.text)
            # raise ValidationError(response.text)    
            return lista_produdctos_registrados
    def consul_id_product(self, code, url):
        # raise ValidationError(codigos)
        lista = []

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ProductConsulta</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"Value\">\r\n                        <_0:val>{code}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

        doc_xml = El.fromstring(xml)
        data_cbpart = []
        # raise ValidationError(response.text)
        for x in doc_xml.iter():
            # print(x.attrib)
            if x.attrib and len(x.attrib) <= 2:
                data_cbpart.append(x.attrib)
            cont = 0

        for part in data_cbpart:
            for cont, value in part.items():
                dic = {
                    cont: value,
                }
            for valida in dic.values():
                lista.append(valida)
        # raise ValidationError(lista)
        return lista[0]
    def update_direccion_entrega(self, order_id,C_BPartner_Location_ID,url):
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:updateData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>UpdatePriceListOrderVente</adin:serviceType>
                            <adin:RecordID>{order_id}</adin:RecordID>
                            <!--Optional:-->
                            <adin:DataRow>
                                <adin:field column="C_BPartner_Location_ID">
                                    <adin:val>{C_BPartner_Location_ID}</adin:val>
                                </adin:field>
                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>dGarcia</adin:user>
                            <adin:pass>dGarcia</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>1000000</adin:ClientID>
                            <adin:RoleID>1000000</adin:RoleID>
                            <adin:OrgID>0</adin:OrgID>
                            <adin:WarehouseID>0</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                        </adin:queryData>
                    </soapenv:Body>
                    </soapenv:Envelope>

                """
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text
    def update_price_list(self, order_id, M_PriceList_ID):
        url = "http://adempiere-qa-engine.iancarina.com.ve/ADInterface/services/ModelADService"
        payload = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
                <soapenv:Header/>
                <soapenv:Body>
                    <adin:updateData>
                        <adin:ModelCRUDRequest>
                            <adin:ModelCRUD>
                            <adin:serviceType>UpdatePriceListOrderVente</adin:serviceType>
                            <adin:RecordID>{order_id}</adin:RecordID>
                            <!--Optional:-->
                            <adin:DataRow>
                                <adin:field column="M_PriceList_ID">
                                    <adin:val>{M_PriceList_ID}</adin:val>
                                </adin:field>
                            </adin:DataRow>
                            </adin:ModelCRUD>
                            <adin:ADLoginRequest>
                            <adin:user>dGarcia</adin:user>
                            <adin:pass>dGarcia</adin:pass>
                            <adin:lang>es_VE</adin:lang>
                            <adin:ClientID>1000000</adin:ClientID>
                            <adin:RoleID>1000000</adin:RoleID>
                            <adin:OrgID>0</adin:OrgID>
                            <adin:WarehouseID>0</adin:WarehouseID>
                            <adin:stage>0</adin:stage>
                            </adin:ADLoginRequest>
                        </adin:ModelCRUDRequest>
                        </adin:queryData>
                    </soapenv:Body>
                    </soapenv:Envelope>

                """
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text

    def conection_url_admpiere(self, company_id):
        record = self.env["web.service.eng"].search([("company_id", "=", company_id)])
        record.url
    @api.onchange('sale_order_line_ids')
    def _onchange_sale_order_line_ids(self):
        
        for rec in self.sale_order_line_ids:
            cantdad = rec.product_uom_qty
            cant_entega = rec.qty_delivered
            if cant_entega <= 0 :
                rec.qty_delivered = rec.product_uom_qty
