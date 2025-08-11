from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pagopa_schema.uuid6 import uuid7

class Base(DeclarativeBase):
    pass

class BaseUUIDModel(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid7, nullable=False, index=True)

# modello fittizio ("stub") solo per soddisfare SQLAlchemy
class IstanzaTipo(Base):
    __tablename__ = "istanza_tipo"
    __table_args__ = {"schema": "istanze"}

    id: Mapped[str] = mapped_column(primary_key=True)