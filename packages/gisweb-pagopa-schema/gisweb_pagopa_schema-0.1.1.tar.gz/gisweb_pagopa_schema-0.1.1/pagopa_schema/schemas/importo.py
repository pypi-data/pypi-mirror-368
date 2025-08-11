from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ImportoBase(BaseModel):
    tipo_id: str
    prog: int
    importo: float
    causale: str | None = None
    capitolo: str | None = None


class ImportoCreate(ImportoBase):
    pagamento_id: UUID
    
class ImportoUpdate(ImportoBase):
    pagamento_id: UUID

class ImportoUpdate(BaseModel):
    importo: float | None = None
    causale: str | None = None
    capitolo: str | None = None


class ImportoRead(ImportoBase):
    id: UUID
    pagamento_id: UUID
    model_config = ConfigDict(from_attributes=True)
