from fastapi import Response
from jinja2 import Environment, PackageLoader, select_autoescape
from zeep import Client
from zeep.transports import Transport
from requests import Session
import base64
import xml.etree.ElementTree as ET

from pagopa_schema.schemas import ISoggetto, IDebito, ConfigPagopaBase
from gisweb_depag.exceptions import DepagServiceError
from gisweb_depag.schemas import AggiornaDovutoRequest, GeneraAvvisoRequest, RicercaDovutiSoggettoRequest, ServiceResponse






env = Environment(
    loader=PackageLoader("gisweb_depag", "templates"),
    autoescape=select_autoescape()
)

class DepagClient:
    def __init__(self, config):
        self.config = config
        session = Session()
        if config.wsUser and config.wsPassword:
            session.auth = (config.wsUser, config.wsPassword)

        self.client = Client(
            wsdl=config.wsUrl,
            transport=Transport(session=session),
        )


    async def PagamentoAvviso(self, soggetto: ISoggetto, debito: IDebito, testXml:bool=True):
                
        test = {
            "chiave": "1a6f2bcb-2481-4381-b93b-1c9ac896a099",
            "tipo_pagatore": "F",
            "codice_pagatore": "STRRRT64A22D969F",
            "anagrafica_pagatore": "ROBERTO STARNINI",
            "causale_versamento": "Pagamenti Prova",
            "data_scadenza": "2025-12-31",
            "importo_totale": 0.1,
            "versamenti": [
                {
                "progressivo": 1,
                "servizio": "DIRITTI_SUAP",
                "causale": "Causale versamento prova",
                "importo": 0.1
                }
            ]
            }

        request = AggiornaDovutoRequest(**test)

        try:
            template = env.get_template("aggiornaDovuto.xml")
            xml = template.render(test)
            xml_clean = "".join(line.strip() for line in xml.splitlines())

            print (xml)
            if testXml:
                return xml
            
            import pdb;pdb.set_trace()

            b64 = base64.b64encode(xml_clean.encode("utf-8")).decode("utf-8")
            response:ServiceResponse = self.client.service.aggiornaDovuto(
                ente='00754860377',
                servizio='DIRITTI_SUAP',
                param=b64
            )
            ret = base64.b64decode(response.param)
            return ret

        except Exception as e:
            raise DepagServiceError(f"Errore in aggiornaDovuto: {e}") from e


    async def eliminaAvvisoPagamento(self, iuv:str):
        try:
            template = env.get_template("eliminaDovuto.xml")
            xml = template.render()
            xml_clean = "".join(line.strip() for line in xml.splitlines())

            b64 = base64.b64encode(xml_clean.encode("utf-8")).decode("utf-8")
            response = self.client.service.eliminaDovuto(
                ente='00754860377',
                servizio='DIRITTI_SUAP',
                param=b64
            )
            # Decodifica e parsing XML
            xml_str = base64.b64decode(response.param).decode("utf-8")
            root = ET.fromstring(xml_str)
            esito = root.findtext("ESITO_OPERAZIONE", default="UNKNOWN")
            codice_errore = root.findtext("CODICE_ERRORE")
            descrizione_errore = root.findtext("DESCRIZIONE_ERRORE")

            # Restituisci struttura coerente per FastAPI
            return {
                "esito": esito,
                "codice_errore": codice_errore,
                "descrizione_errore": descrizione_errore,
            }

        except Exception as e:
            raise DepagServiceError(f"Errore in ricercaDovutiSoggetto: {e}") from e
        

    async def ricerca_dovuti_soggetto(self, request: RicercaDovutiSoggettoRequest = None, testXml: bool = False):
        try:
            template = env.get_template("ricercaDovutiSoggetto.xml")
            xml = template.render()
            xml_clean = "".join(line.strip() for line in xml.splitlines())

            if testXml:
                return xml

            import pdb;pdb.set_trace()
            b64 = base64.b64encode(xml_clean.encode("utf-8")).decode("utf-8")
            response = self.client.service.ricercaDovutiSoggetto(
                ente='00754860377',
                codiceSoggetto='STRRRT64A22D969F',
                param=b64
            )
            ret = base64.b64decode(response.param)
            return ret
        except Exception as e:
            raise DepagServiceError(f"Errore in ricercaDovutiSoggetto: {e}") from e
        
        
    async def leggi_dovuto(self, request: RicercaDovutiSoggettoRequest = None, testXml: bool = False):
        try:
            template = env.get_template("leggiDovuto.xml")
            xml = template.render()
            xml_clean = "".join(line.strip() for line in xml.splitlines())

            if testXml:
                return xml

            import pdb;pdb.set_trace()
            b64 = base64.b64encode(xml_clean.encode("utf-8")).decode("utf-8")
            response = self.client.service.leggiDovuto(
                ente='00754860377',
                servizio='DIRITTI_SUAP',
                param=b64
            )
            ret = base64.b64decode(response.param)
            return ret
        except Exception as e:
            raise DepagServiceError(f"Errore in ricercaDovutiSoggetto: {e}") from e


    async def genera_avviso(self, request: GeneraAvvisoRequest = None, testXml: bool = False):
        try:
            template = env.get_template("generaAvviso.xml")
            xml = template.render()
            xml_clean = "".join(line.strip() for line in xml.splitlines())

            if testXml:
                return xml

            import pdb;pdb.set_trace()
            b64 = base64.b64encode(xml_clean.encode("utf-8")).decode("utf-8")
            response = self.client.service.generaAvviso(
                ente='00754860377',
                servizio='DIRITTI_SUAP',
                param=b64
            )
            
            # Step 1: decode base64 -> XML string
            xml_str = base64.b64decode(response.param).decode("utf-8")

            # Step 2: parse XML and extract AVVISO base64
            root = ET.fromstring(xml_str)
            avviso_b64 = root.findtext(".//AVVISO")
            if not avviso_b64:
                raise DepagServiceError("Nessun contenuto <AVVISO> trovato nella risposta")

            # Step 3: decode AVVISO content
            pdf_bytes = base64.b64decode(avviso_b64)
            

            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": 'attachment; filename="avviso_pagamento.pdf"'
                },
            )            

        except Exception as e:
            raise DepagServiceError(f"Errore in genera avviso: {e}") from e