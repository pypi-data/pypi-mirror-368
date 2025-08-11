from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy import String
from sqlmodel import SQLModel
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship, DateTime, ARRAY, ForeignKey, Column, Boolean, false
from pagopa_schema.uuid6 import uuid7

class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )
    
class BaseIDModel(SQLModel):
    id: int = Field(
        primary_key=True,
        nullable=False,
        default=None
    )
    
class ImportoBase(SQLModel):
    tipo_id: str | None = Field(sa_column=Column(ForeignKey("pagopa.importo_tipo.id"), nullable=False, default=None))
    prog: int
    importo: float
    causale: str | None = None
    capitolo: str | None = None


class PagamentoBase(SQLModel):
    
    document_id: UUID | None = Field(nullable=False, index=True, default=None)
    parent_id: UUID | None = None
    tipo_id: str | None = Field(sa_column=Column(ForeignKey("pagopa.pagamento_tipo.id"), nullable=False, default=None), default="VARIE")

    idpos: str | None = None #max 256
    iddeb: str | None = None #max 256
    iuv: str | None = None
    modello:str | None = None #Modello 1 o 3 
    servizio: str | None = None    #codice servizio previsto da jppa (negozio di regione)
    importo: float | None = None
    pagato: float | None = None
    causale: str | None = None # max 140 
    data_inizio: date | None = None
    data_scadenza: date | None = None
    data_scadenza_avviso: date | None = None
    tipo_scadenza: str | None = None
    testo_scadenza: str | None = None

    gg_scadenza: int | None = None

    data_pagamento: date | None = None
    ora_pagamento: str | None = None
    
    attestante: str | None = None
    data_inserimento: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True), default=None)

    stato:str | None = None #Pagata NonPagata PagataParzialmente
    esito: str | None = None #esito operazione
        
    accertamento: str | None = None #Codice accertamento assegnato alla posizione debitoria
    gruppo: str | None = None #gruppo di pagamenti previsto da jppa
    ordinamento: int | None = None
    rata: int | None = None
    tassonomia: str | None = None

    soggetto: str | None = None #F/G fisica o giuridica
    cf_piva: str | None = None #piva o cf
    nome: str  | None = None
    cognome: str  | None = None
    denominazione: str | None = None
    indirizzo: str | None = None
    civico: str | None = None
    cap: str | None = None
    loc: str | None = None
    prov: str | None = None
    nazione: str | None = None
    email: str  | None = None
    
    
    azione: str  | None = None
    info: str | None = None ### log con errori o altro
    
class ConfigPagopaBase(SQLModel):
    modulo: str = Field(sa_column=Column(ForeignKey("istanze.istanza_tipo.id"), nullable=False, default=None), default=None)
    pagamento_tipo: str | None = Field(sa_column=Column(ForeignKey("pagopa.pagamento_tipo.id"), nullable=False, default=None), default="VARIE")
    importo_tipo: str | None = Field(sa_column=Column(ForeignKey("pagopa.importo_tipo.id"), nullable=False, default=None), default=None)
    capitolo: str | None = None
    descrizione: str | None = None
    importo: float | None = None
    azione: str | None = None
    attivo: bool | None = Field(sa_column=Column(Boolean, server_default=false(),nullable=False), default=True)
    ordine: int | None = None
    gg_scadenza: int | None = None

class ConfigPagopa(BaseUUIDModel, ConfigPagopaBase, table=True):
    __table_args__ = {'schema': 'pagopa'}
    __tablename__ = 'config'

    pagamento: Optional["PagamentoTipo"] = Relationship(
        sa_relationship_kwargs={
            "lazy":"joined",
            "primaryjoin": "ConfigPagopa.pagamento_tipo==PagamentoTipo.id"
        }
    )
    importo_def: Optional["ImportoTipo"] = Relationship(
        sa_relationship_kwargs={
            "lazy":"joined",
            "primaryjoin": "ConfigPagopa.importo_tipo==ImportoTipo.id"
        }
    )


class PagamentoTipo(SQLModel, table=True):
    __table_args__ = {'schema': 'pagopa'}
    __tablename__ = 'pagamento_tipo'
    id: str | None = Field(default=None, nullable=False, primary_key=True)
    descrizione: str | None

class ImportoTipo(SQLModel, table=True):
    __table_args__ = {'schema': 'pagopa'}
    __tablename__ = 'importo_tipo'
    id: str | None = Field(default=None, nullable=False, primary_key=True)
    descrizione: str | None

class Pagamento(BaseUUIDModel, PagamentoBase, table=True):  
    __table_args__ = {'schema': 'pagopa'}
    __tablename__ = 'pagamento'
    readers: list[str] | None = Field(sa_column=Column(ARRAY(String), nullable=True), default=None)
    updated_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True), default=None)
    updated_by_id: str | None = None
    created_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True), nullable=True), default_factory=datetime.utcnow)
    created_by_id: str | None  = None
    removed: bool | None = Field(sa_column=Column(Boolean, server_default=false(),nullable=False), default=False)
    
    tipo_pagamento: PagamentoTipo = Relationship(
        sa_relationship_kwargs={
            "lazy":"joined",
            "primaryjoin": "Pagamento.tipo_id==PagamentoTipo.id"
        }
    )
    importi: list["Importo"] = Relationship(
        sa_relationship_kwargs={
            "lazy":"selectin",
            "primaryjoin": "Pagamento.id==Importo.pagamento_id",
            "order_by": "(Importo.prog)",
        }, back_populates="pagamento"
    )    
    

class Importo(BaseUUIDModel, ImportoBase, table=True): 
    __table_args__ = {'schema': 'pagopa'}
    __tablename__ = 'importo'
    pagamento_id: UUID | None = Field(sa_column=Column(ForeignKey("pagopa.pagamento.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, default=None))
    pagamento: Optional[Pagamento] = Relationship(sa_relationship_kwargs={"lazy":"selectin"}, back_populates="importi")    
    tipo_importo: Optional[ImportoTipo] = Relationship(
        sa_relationship_kwargs={
            "lazy":"joined",
            "primaryjoin": "Importo.tipo_id==ImportoTipo.id"
        }
    )
