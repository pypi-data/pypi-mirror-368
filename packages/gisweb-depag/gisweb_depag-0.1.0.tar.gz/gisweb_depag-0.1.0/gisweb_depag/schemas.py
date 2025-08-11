from pydantic import BaseModel, Field
from typing import List
import datetime


class SingoloVersamento(BaseModel):
    progressivo: int = Field(..., alias="PROGRESSIVO")
    servizio: str = Field(..., alias="SERVIZIO")
    causale: str = Field(..., alias="CAUSALE")
    importo: float = Field(..., alias="IMPORTO")
    dati_riscossione: str = Field(..., alias="DATI_RISCOSSIONE")


class AggiornaDovutoRequest(BaseModel):
    chiave: str = Field(..., alias="CHIAVE")
    tipo_pagatore: str = Field(..., alias="TIPO_PAGATORE")  # "F" o "G"
    codice_pagatore: str = Field(..., alias="CODICE_PAGATORE")
    anagrafica_pagatore: str = Field(..., alias="ANAGRAFICA_PAGATORE")
    causale_versamento: str = Field(..., alias="CAUSALE_VERSAMENTO")
    data_scadenza: str = Field(..., alias="DATA_SCADENZA")  # in formato YYYY-MM-DD
    importo_totale: float = Field(..., alias="IMPORTO_TOTALE")
    quote_mb: str = Field(..., alias="QUOTE_MB")  # "SI" o "NO"
    versamenti: List[SingoloVersamento] = Field(..., alias="SINGOLO_VERSAMENTO")

    class Config:
        populate_by_name = True



class RicercaDovutiSoggettoRequest(BaseModel):
    codiceSoggetto: str
    param: str

class GeneraAvvisoRequest(BaseModel):
    codiceSoggetto: str
    param: str

class ServiceResponse(BaseModel):
    ente: str | None = None
    param: str | None = None
    
    
class AggiornaDovutoRequest(BaseModel):
    pass
