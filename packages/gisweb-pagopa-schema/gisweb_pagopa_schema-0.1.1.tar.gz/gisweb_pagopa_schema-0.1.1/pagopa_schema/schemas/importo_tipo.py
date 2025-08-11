from pydantic import BaseModel, ConfigDict


class ImportoTipoBase(BaseModel):
    descrizione: str | None = None


class ImportoTipoCreate(ImportoTipoBase):
    id: str


class ImportoTipoRead(ImportoTipoCreate):
    model_config = ConfigDict(from_attributes=True)
