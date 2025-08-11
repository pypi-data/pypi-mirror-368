from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import String
from sqlmodel import SQLModel
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship, DateTime, ARRAY, ForeignKey, Column, Boolean, false
from pagopa_schema.models import Importo, ImportoBase, ImportoTipo, PagamentoBase
from pagopa_schema.uuid6 import uuid7


    
class IImporto(BaseModel):
    tipo_id: str
    prog: int | None = None
    causale: str | None = None
    importo: float
    capitolo: str | None = None
    

class ISoggetto(BaseModel):
    tipo: Literal["F", "G"]
    codice: str
    nome: str | None
    cognome: str | None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    loc: str | None = None
    prov: str | None = None
    nazione: str | None = None
    email: str | None

class IChiaveDebito(BaseModel):
    idpos: str | None = None
    iddeb: str | None = None
    codice: str | None = None #codice servizio (tipo pagamento)
    
class IDebito(IChiaveDebito):
    iuv: str | None = None
    dettaglio: str | None = Field(None, max_length=1000) #descrizione del pagamento(causale lunga)
    gruppo: str | None = None
    ordinamento: int | None = None
    data_inizio: date
    data_scadenza: date | None = None
    data_scadenza_avviso: date | None = None
    testo_scadenza: str | None = Field(None, max_length=50) #Testo in sostituzione della data di scadenza
    importo: float
    causale: str | None = Field(None, max_length=140) #causale passata a pagopa
    importi: list[IImporto]



    
class IConfigAzione(BaseModel):
    id : UUID
    azione: str
    importo: float
    pagamento_tipo: str
    iddeb: str
    causale: str
    importi: list[ImportoBase]

class IImportoRead(ImportoBase):
    tipo_importo: ImportoTipo | None = None
    

class IImportoCreate(ImportoBase):
    pagamento_id: UUID | None = None
    
class IPagamentoRead(PagamentoBase):
    id: UUID
    importi: list[IImportoRead]
    
class IPagamentoAzione(SQLModel):
    id: UUID
    tipo_id: str | None = None
    idpos: str | None = None
    importo: float  | None = None   
    causale: str | None = None
    gg_scadenza: int | None = None
    importi: list[IImportoRead]
    
class IPagamentoCreate(PagamentoBase):
    id:UUID | None = None
    red_url: str | None = None
    wisp_url: str | None = None
    importi: list[Importo]
    readers: list[str] | None = None
    
    
class IPagamentoUpdate(PagamentoBase):
    id: UUID | None = None

class IImportoUpdate(ImportoBase):
    id: UUID
    
class IPagamentoImportiCreate(PagamentoBase):
    id: UUID
    readers: list[str] | None = None
    importi: list[Importo]
    
class IPagamentoImportiRead(PagamentoBase):
    id: UUID
    importi: list[IImportoRead]
    
class IPagamentoInfo(BaseModel):
    tipo: str | None
    idpos: str | None = None #max 256
    iddeb: str | None = None #max 256
    iuv: str | None = None
    descrizione: str | None = None #max 1000
    modello:str | None = None #Modello 1 o 3 
    importo: float | None = None
    pagato: float | None = None
    causale: str | None = None # max 140 
    data_pagamento: date | None = None
    ora_pagamento: str | None = None
    stato:str | None = None #Pagata NonPagata PagataParzialmente
    esito: str | None = None #esito operazione
    accertamento: str | None = None #Codice accertamento assegnato alla posizione debitoria
    tassonomia: str | None = None
    soggetto: str | None = None #F/G fisica o giuridica
    cf_piva: str | None = None #piva o cf
    nome: str | None
    cognome: str | None
    denominazione: str | None = None
    email: str | None
    azione: str | None
    
    
    

    

    


    
class IDataPagoPa(BaseModel):
    soggetto: ISoggetto
    debito: IDebito

class IEsito(BaseModel):
    esito: Literal["OK", "ERROR"]
    messaggio: str | None = None

class IConfigPagoPa(BaseModel):
    wsUrl: str
    wsUser: str
    wsPassword: str
    wsPrintUrl: str | None = None
    logoUrl: str | None = None
    codiceIpa: str | None = None
    codiceEnte: str | None = None
    codiceServizio: str | None = None
    notificaOK: str | None = None
    notificaKO: str | None = None
    notificaPagamento: str | None = None



class RicercaDovutiSoggettoRequest(BaseModel):
    ente: str
    codiceSoggetto: str
    param: str


class Output(BaseModel):
    ente: str | None = None
    param: str | None = None
