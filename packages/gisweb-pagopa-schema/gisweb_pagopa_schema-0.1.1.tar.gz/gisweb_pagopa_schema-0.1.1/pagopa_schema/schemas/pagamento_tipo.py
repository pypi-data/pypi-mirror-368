from pydantic import BaseModel, ConfigDict


class PagamentoTipoBase(BaseModel):
    descrizione: str | None = None


class PagamentoTipoCreate(PagamentoTipoBase):
    id: str


class PagamentoTipoRead(PagamentoTipoCreate):
    model_config = ConfigDict(from_attributes=True)
