# Respaldo de Boton Impoprt Adempiere
def import_adempiere(self):
    listarif = []
    lsita_raise = []
    lista_company = []
    for rec in self:
        for rif in rec.sale_order_line_ids:
            if rif.vat not in listarif:
                listarif.append(rif.vat)
            if rif.destination_company_id not in lista_company:
                lista_company.append(rif.destination_company_id.name)
        # raise ValidationError(lista_company)

        for rif_F in listarif:
            admpiere_partner_id = rec.consul_cb_partner(CI=rif_F)

            partnet_adem = admpiere_partner_id['partner']
            # raise ValidationError(rec.env.user.login)
            user_admpiere = rec.consul_user(
                code=rec.env.user.login)

            # raise ValidationError(user_admpiere['name'])
            # LOGUE DE USUARIO CREDENCIALES
            user = user_admpiere['value']
            clave = user_admpiere['password']
            client_id = '1000000'
            role_id = user_admpiere['rol_id']
            org_id = user_admpiere['ad_org_id']
            WarehouseID = user_admpiere['almacen']

            DocTypeTarget = '1000675'
            # LOGUE DE USUARIO CREDENCIALES
            # Crando LA ORDEN DE VENTA EN ADEMPIERE
            ad_client = "1000000"
            c_order_admpiere = rec.web_service_c_order(user=user, clave=clave, ClientID=client_id, RoleID=role_id,
                                                       OrgID=org_id, WarehouseID=WarehouseID, C_BPartner_ID=partnet_adem, C_Campaign_ID='1000000', C_Project_ID='1000018', M_Warehouse_ID=WarehouseID, Description="OKOK VASD", C_DocTypeTarget_ID=DocTypeTarget, AD_Client_ID=ad_client)
            order_filter_id = c_order_admpiere[0]
            if c_order_admpiere:
                update_pricelis = rec.update_price_list(
                    order_id=order_filter_id, M_PriceList_ID='1000078')
                # raise ValidationError(c_order_admpiere)
                lista_produdctos_registrados = rec.create_order_line(order_id=order_filter_id, user=user, clave=clave,
                                                                     ClientID=client_id, RoleID=role_id, OrgID=org_id, WarehouseID=WarehouseID)
        # raise ValidationError(update_pricelis)

        if lista_produdctos_registrados:
            ids_order_line = []
            for id_register in lista_produdctos_registrados:
                id_order_line = rec.get_data_response(xml=id_register)
                ids_order_line.append(id_order_line)
            if ids_order_line:
                rec.state = 'import_ademp'

        else:
            raise ValidationError("No hay vida")

# import requests
# # from xml.etree.ElementTree import parse, Element
# import xml.etree.ElementTree as El
# import tempfile
# import hashlib
# # from cryptography.fernet import Fernet
# # import pandas as pd


# def web_service_c_order(user, clave, ClientID, RoleID, OrgID, WarehouseID, AD_Client_ID, AD_Org_ID, C_DocTypeTarget_ID, Description, C_BPartner_ID, C_Campaign_ID, C_Project_ID, M_Warehouse_ID):
#     url = "http://adempiere-qa-engine.iancarina.com.ve/ADInterface/services/ModelADService"

#     payload = f'''
#     <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:adin="http://3e.pl/ADInterface">
#     <soapenv:Header/>
#     <soapenv:Body>
#         <adin:createData>
#             <adin:ModelCRUDRequest>
#                 <adin:ModelCRUD>
#                 <adin:serviceType>CreateOrderPedidos</adin:serviceType>
#                 <adin:TableName>C_Order</adin:TableName>
#                 <adin:RecordID>0</adin:RecordID>

#                 <adin:Action>Create</adin:Action>
#                 <adin:PageNo>0</adin:PageNo>
#                 <!--Optional:-->
#                 <adin:DataRow>

#                     <adin:field column="AD_Client_ID">
#                         <adin:val>{AD_Client_ID}</adin:val>
#                     </adin:field>
#                     <adin:field column="AD_Org_ID">
#                         <adin:val>{AD_Org_ID}</adin:val>
#                     </adin:field>
#                     <adin:field column="C_DocTypeTarget_ID">
#                         <adin:val>{C_DocTypeTarget_ID}</adin:val>
#                     </adin:field>
#                     <adin:field column="Description">
#                         <adin:val>{Description}</adin:val>
#                     </adin:field>

#                     <adin:field column="C_BPartner_ID">
#                         <adin:val>{C_BPartner_ID}</adin:val>
#                     </adin:field>

#                     <adin:field column="C_Campaign_ID">
#                         <adin:val>{C_Campaign_ID}</adin:val>
#                     </adin:field>
#                     <adin:field column="C_Project_ID">
#                         <adin:val>{C_Project_ID}</adin:val>
#                     </adin:field>
#                     <adin:field column="M_Warehouse_ID">
#                         <adin:val>{M_Warehouse_ID}</adin:val>
#                     </adin:field>


#                 </adin:DataRow>
#                 </adin:ModelCRUD>
#                 <adin:ADLoginRequest>
#                 <adin:user>{user}</adin:user>
#                 <adin:pass>{clave}</adin:pass>
#                 <adin:lang>es_VE</adin:lang>
#                 <adin:ClientID>{ClientID}</adin:ClientID>
#                 <adin:RoleID>{RoleID}</adin:RoleID>
#                 <adin:OrgID>{OrgID}</adin:OrgID>
#                 <adin:WarehouseID>{WarehouseID}</adin:WarehouseID>
#                 <adin:stage>0</adin:stage>
#                 </adin:ADLoginRequest>
#             </adin:ModelCRUDRequest>
#         </adin:createData>
#     </soapenv:Body>
#     </soapenv:Envelope>

#     '''
#     headers = {
#         'Content-Type': 'application/xml'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     print(response.text)
#     return True


# def consul_cb_partner(rif):

#     url = "http://adempiere-engine.iancarina.com.ve//ADInterface/services/ModelADService"

#     payload = f'''<?xml version='1.0' encoding='UTF-8'?> <soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>CBPartnerConsul</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"TaxID\">\r\n                        <_0:val>{rif}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>'''
#     headers = {
#         'Content-Type': 'application/xml'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     temp = tempfile.TemporaryFile()
#     xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

#     doc_xml = El.fromstring(xml)
#     doc_xml.items()
#     # print(doc_xml.iter())
#     data_cbpart = []
#     dic = {}
#     cont = 0
#     for x in doc_xml.iter():

#         # print(x.attrib)
#         if x.attrib and len(x.attrib) <= 2:
#             data_cbpart.append(x.attrib)
#         cont = 0
#         lista = []
#     for part in data_cbpart:
#         for cont, value in part.items():

#             dic = {
#                 cont: value,
#                 cont: value,
#                 cont: value,
#                 cont: value,
#             }

#         for valida in dic.values():
#             lista.append(valida)

#     diccio = {
#         'partner': lista[0],
#         'taxid': lista[1],
#         'name': lista[2],
#         'ad_org_id': lista[3]

#     }

#     return diccio


# def consul_user(code):

#     url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

#     payload = f'''<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConsulUsuario</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"Value\">\r\n                        <_0:val>{code}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>'''
#     headers = {
#         'Content-Type': 'application/xml'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     # print(response.text)
#     xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

#     doc_xml = El.fromstring(xml)
#     doc_xml.items()
#     print(doc_xml.items)
#     data_cbpart = []
#     dic = {}
#     cont = 0
#     for x in doc_xml.iter():

#         # print(x.attrib)
#         if x.attrib and len(x.attrib) <= 2:
#             data_cbpart.append(x.attrib)
#         cont = 0
#         lista = []
#     for part in data_cbpart:
#         for cont, value in part.items():

#             dic = {
#                 cont: value,

#             }

#         for valida in dic.values():
#             lista.append(valida)
#     # print(lista)
#     consul_org = consul_organiz_user_acc(org_acc=lista[3])
#     org_asignado = consul_org[0]
#     # print(lista)
#     diccio = {
#         'ad_org_id': org_asignado,
#         'name': lista[0],
#         'value': lista[1],
#         'password': lista[2],
#         'user_id': lista[3],
#         'org_tans': lista[4],

#     }

#     return diccio


# def consul_organiz_user_acc(org_acc):
#     url = "http://adempiere-engine.iancarina.com.ve/ADInterface/services/ModelADService"

#     payload = f'''<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:_0=\"http://3e.pl/ADInterface\">\r\n   <soapenv:Header/>\r\n   <soapenv:Body>\r\n     <_0:queryData>\r\n       <_0:ModelCRUDRequest>\r\n         <_0:ModelCRUD>\r\n           <_0:serviceType>ConusultOrganizAcceso</_0:serviceType>\r\n          <_0:DataRow>\r\n            <_0:field column=\"AD_User_ID\">\r\n                        <_0:val>{org_acc}</_0:val>\r\n            </_0:field>\r\n          </_0:DataRow>\r\n         </_0:ModelCRUD>\r\n         <_0:ADLoginRequest>\r\n           <_0:user>dGarcia</_0:user>\r\n           <_0:pass>dGarcia</_0:pass>\r\n           <_0:lang>es_VE</_0:lang>\r\n           <_0:ClientID>1000000</_0:ClientID>\r\n           <_0:RoleID>1000000</_0:RoleID>\r\n           <_0:OrgID>0</_0:OrgID>\r\n           <_0:WarehouseID>0</_0:WarehouseID>\r\n           <_0:stage>0</_0:stage>\r\n         </_0:ADLoginRequest>\r\n       </_0:ModelCRUDRequest>\r\n     </_0:queryData>\r\n   </soapenv:Body>\r\n </soapenv:Envelope>'''
#     headers = {
#         'Content-Type': 'application/xml'
#     }

#     response = requests.request("POST", url, headers=headers, data=payload)

#     xml = "<?xml version='1.0' encoding='UTF-8'?>" + response.text

#     doc_xml = El.fromstring(xml)
#     doc_xml.items()
#     # print(doc_xml.iter)
#     data_cbpart = []
#     dic = {}
#     cont = 0
#     for x in doc_xml.iter():

#         # print(x.attrib)
#         if x.attrib and len(x.attrib) <= 2:
#             data_cbpart.append(x.attrib)
#         cont = 0
#         lista = []
#     for part in data_cbpart:
#         for cont, value in part.items():

#             dic = {
#                 cont: value,

#             }

#         for valida in dic.values():
#             lista.append(valida)
#     # print(lista)
#     return lista


# # def role_user_id():
# consul_user(code="MYGonzalez")
# # consul_organiz_user_acc(org_acc='1026161')
# # print(dicc['value'])
# # consul_cb_partner()
