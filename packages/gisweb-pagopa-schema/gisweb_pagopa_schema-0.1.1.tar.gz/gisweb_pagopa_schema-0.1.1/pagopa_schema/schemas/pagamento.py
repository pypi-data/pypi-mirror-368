from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime, date
from typing import List, Literal
from pagopa_schema.models.importo import Importo
from pagopa_schema.schemas.importo import ImportoRead


class ISettingsPagoPa(BaseModel):
    wsUrl: str
    wsUser: str
    wsPassword: str
    wsPrintUrl: str
    logoUrl: str
    codiceIpa: str
    codiceServizio: str
    notificaOK: str | None = None
    notificaKO: str | None = None
    notificaPagamento: str

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
    importi: list[ImportoRead]

class PagamentoBase(BaseModel):
    document_id: UUID
    parent_id: UUID | None = None
    tipo_id: str

    importo: float | None = None
    pagato: float | None = None
    causale: str | None = None
    data_inizio: date | None = None
    data_scadenza: date | None = None
    data_scadenza_avviso: date | None = None
    tipo_scadenza: str | None = None
    testo_scadenza: str | None = None
    gg_scadenza: int | None = None
    data_pagamento: date | None = None
    ora_pagamento: str | None = None

    attestante: str | None = None
    stato: str | None = None
    esito: str | None = None
    accertamento: str | None = None
    gruppo: str | None = None
    ordinamento: int | None = None
    rata: int | None = None
    tassonomia: str | None = None

    soggetto: str | None = None
    cf_piva: str | None = None
    nome: str | None = None
    cognome: str | None = None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    loc: str | None = None
    prov: str | None = None
    nazione: str | None = None
    email: str | None = None
    azione: str | None = None
    info: str | None = None


class PagamentoCreate(PagamentoBase):
    pass


class PagamentoUpdate(BaseModel):
    importo: float | None = None
    pagato: float | None = None
    stato: str | None = None
    esito: str | None = None
    azione: str | None = None
    info: str | None = None


class PagamentoRead(PagamentoBase):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    readers: List[str] | None = None

    model_config = ConfigDict(from_attributes=True)

class IPagamentoAzione(BaseModel):
    id: UUID
    tipo_id: str | None = None
    descrizione: str | None = None
    idpos: str | None = None
    importo: float  | None = None   
    causale: str | None = None
    gg_scadenza: int | None = None
    importi: list[ImportoRead]
    
class IPagamentoImportiCreate(PagamentoBase):
    id: UUID
    readers: list[str] | None = None
    importi: list[ImportoRead]
    
class IPagamentoImportiRead(PagamentoBase):
    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None
    readers: List[str] | None = None
    importi: list[ImportoRead]
    
class IEsito(BaseModel):
    esito: Literal["OK", "ERROR"]
    messaggio: str | None = None