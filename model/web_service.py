import requests
import xml.etree.ElementTree as El
from werkzeug import urls
from odoo import api, fields, models, _

from odoo.exceptions import ValidationError


class WebServiceEng(models.Model):
    _name = "web.service.eng"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]

    name = fields.Char(strig="Nombre de Conceccio")

    url = fields.Char(string="Url Engine")

    description = fields.Text(string="Description")

    code = fields.Char(string="Code Conection")

    company_id = fields.Many2one(
        "res.company",
        string="company",
    )
    oredenes_carga_ids = fields.One2many(
        "freight.order", "crear_c_order_in_id", string="Ordenes De Carga"
    )

    @api.constrains("url", "company_id")
    def _check_url_code(self):
        for rec in self:
            if rec.url:
                identi = rec.url.find("qa")
                rang = identi + 2
                rec.code = rec.company_id.name + "_" + rec.url[identi:rang].upper()

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
        url,
    ):
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
                    <adin:WarehouseID>{WarehouseID}</adin:WarehouseID>
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
    def dd_order_create(
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
        M_Warehouse_ID,
        url,
    ):
        payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
        <soapenv:Header/>
        <soapenv:Body>
            <adin:createData>
                <adin:ModelCRUDRequest>
                    <adin:ModelCRUD>
                    <adin:serviceType>CreateOrderDistribucion</adin:serviceType>
                    <adin:TableName>DD_Order</adin:TableName>
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
                        <adin:field column="C_DocType_ID">
                            <adin:val>{C_DocTypeTarget_ID}</adin:val>
                        </adin:field>
                        <adin:field column="Description">
                            <adin:val>{Description}</adin:val>
                        </adin:field>
                        <adin:field column="C_BPartner_ID">
                            <adin:val>{C_BPartner_ID}</adin:val>
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

    def consul_cb_partner(self, CI, url):
        # recordpro = self.env['web_service'].search(
        #     [('code', '=', 'Iancarina C.A_')])
        # url = recordpro.url
        # raise ValidationError(url)
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

    def consul_user(self, code, url):
        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConsulUsuario</_0:serviceType>\r\n          <_0:DataRow>\r\n       <_0:field column=\"IsActive\">\r\n                        <_0:val>Y</_0:val>\r\n            </_0:field>\r\n            <_0:field column=\"Value\">\r\n                        <_0:val>{code}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
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
        # raise ValidationError(response.text)
        consul_org = self.consul_organiz_user_acc(org_acc=lista[0],url=url)
        consul_rol = self.consul_rol_user(user_id=lista[0],url=url)
        # raise ValidationError(consul_org)
        org_asignado = consul_org[0]
        consul_alma = self.consul_almacen_user(org_id=org_asignado,url=url)
        consul_alma.sort()
        # raise ValidationError(consul_alma)

        # raise ValidationError(consul_tipodc)
        # print(lista)
        diccio = {
            "almacen": consul_alma[0],
            "rol_id": consul_rol[0],
            "ad_org_id": org_asignado,
            "user_id": lista[0],
            "name": lista[1],
            "value": lista[2],
        }

        return diccio

    def consul_organiz_user_acc(self, org_acc, url):
        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConusultOrganizAcceso</_0:serviceType>\r\n          <_0:DataRow>\r\n <_0:field column=\"IsActive\">\r\n                        <_0:val>Y</_0:val>\r\n            </_0:field>\r\n            <_0:field column=\"AD_User_ID\">\r\n                        <_0:val>{org_acc}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
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

    def consul_rol_user(self, user_id, url):
        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>RoleUserAccs</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"IsActive\">\r\n                        <_0:val>Y</_0:val>\r\n            </_0:field>\r\n <_0:field column=\"AD_User_ID\">\r\n                        <_0:val>{user_id}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        rol_user = self.get_data_response(xml=xml)
        return rol_user

    def consul_almacen_user(self, org_id,url):
        # url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

        payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>AlmacenIDAcssLog</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"AD_Org_ID\">\r\n                        <_0:val>{org_id}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
        headers = {"Content-Type": "application/xml"}

        response = requests.request("POST", url, headers=headers, data=payload)

        xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
        almacen_id = self.get_data_response(xml=xml)
        return almacen_id

    def consul_documet_type(self, org_id, typebase):
        url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

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

                        <adin:field column="AD_Org_ID">
                            <adin:val>{org_id}</adin:val>
                        </adin:field>
                        <adin:field column="C_DocBaseType_ID">
                            <adin:val>{typebase}</adin:val>
                        </adin:field>
                        <adin:field column="IsSOTrx">
                            <adin:val>Y</adin:val>
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
                lista_code_pr.append(codigo_producto[:indice])
            # raise ValidationError(lista_code_pr)
            producto_ad_ids = rec.consul_id_product(codigos=lista_code_pr)
            for producto in producto_ad_ids:
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
                                    <adin:val>{order_id}</adin:val>
                                </adin:field>     
                                <adin:field column="M_Product_ID">
                                    <adin:val>{producto}</adin:val>
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
            return lista_produdctos_registrados

    def consul_id_product(self, codigos, url):
        # raise ValidationError(codigos)
        lista = []
        for code in codigos:
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
        return lista

    def update_price_list(self, order_id, M_PriceList_ID, url):
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

    def conection_url_admpiere(self, company):
        for rec in self:
            if rec.company_id == company:
                return rec.url
            else:
                return ValidationError("No Tiene Url la Compañia")
    def lista_precio(self, price_list):
        for rec in self:
            if rec.name == 'IANCARINA C.A PRO':
                url= rec.url  
                payload = f"""<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ListaPrecio</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"Name\">\r\n                        <_0:val>{price_list}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>"""
                headers = {"Content-Type": "application/xml"}
                response = requests.request("POST", url, headers=headers, data=payload)
                xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text
                id_price_list = self.get_data_response(xml=xml)
        # raise ValidationError(id_price_list)
        return id_price_list