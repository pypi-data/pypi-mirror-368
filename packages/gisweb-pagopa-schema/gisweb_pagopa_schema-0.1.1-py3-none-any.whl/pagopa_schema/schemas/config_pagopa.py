from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ConfigPagopaBase(BaseModel):
    modulo: str
    pagamento_tipo: str | None = "VARIE"
    importo_tipo: str | None = None
    capitolo: str | None = None
    descrizione: str | None = None
    importo: float | None = None
    azione: str | None = None
    attivo: bool = True
    ordine: int | None = None
    gg_scadenza: int | None = None


class ConfigPagopaCreate(ConfigPagopaBase):
    pass


class ConfigPagopaUpdate(BaseModel):
    descrizione: str | None = None
    importo: float | None = None
    attivo: bool | None = None
    ordine: int | None = None
    gg_scadenza: int | None = None


class ConfigPagopaRead(ConfigPagopaBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
