from typing import Optional
from uuid import UUID
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseUUIDModel
from .importo_tipo import ImportoTipo


class Importo(BaseUUIDModel):
    __tablename__ = "importo"
    __table_args__ = {"schema": "pagopa"}

    tipo_id: Mapped[str] = mapped_column(ForeignKey("pagopa.importo_tipo.id"), nullable=False)
    prog: Mapped[int] = mapped_column(Integer, nullable=False)
    importo: Mapped[float] = mapped_column(Float, nullable=False)
    causale: Mapped[str | None] = mapped_column(String, nullable=True)
    capitolo: Mapped[str | None] = mapped_column(String, nullable=True)

    pagamento_id: Mapped[UUID] = mapped_column(ForeignKey("pagopa.pagamento.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    pagamento: Mapped[Optional["Pagamento"]] = relationship("Pagamento", back_populates="importi", lazy="selectin")
    tipo_importo: Mapped[ImportoTipo | None] = relationship(
        "ImportoTipo",
        lazy="joined",
        primaryjoin="Importo.tipo_id == foreign(ImportoTipo.id)"
    )