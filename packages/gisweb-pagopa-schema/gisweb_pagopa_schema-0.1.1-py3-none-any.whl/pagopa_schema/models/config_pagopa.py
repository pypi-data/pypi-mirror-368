from sqlalchemy import String, Float, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseUUIDModel
from .pagamento_tipo import PagamentoTipo
from .importo_tipo import ImportoTipo


class ConfigPagopa(BaseUUIDModel):
    __tablename__ = "config"
    __table_args__ = {"schema": "pagopa"}

    modulo: Mapped[str] = mapped_column(ForeignKey("istanze.istanza_tipo.id"), nullable=False)
    pagamento_tipo: Mapped[str | None] = mapped_column(ForeignKey("pagopa.pagamento_tipo.id"), nullable=False, default="VARIE")
    importo_tipo: Mapped[str | None] = mapped_column(ForeignKey("pagopa.importo_tipo.id"), nullable=False)
    capitolo: Mapped[str | None] = mapped_column(String, nullable=True)
    descrizione: Mapped[str | None] = mapped_column(Text, nullable=True)
    importo: Mapped[float | None] = mapped_column(Float, nullable=True)
    azione: Mapped[str | None] = mapped_column(String, nullable=True)
    attivo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    ordine: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gg_scadenza: Mapped[int | None] = mapped_column(Integer, nullable=True)

    pagamento: Mapped[PagamentoTipo | None] = relationship(
        "PagamentoTipo",
        lazy="joined",
        viewonly=True,
        primaryjoin="ConfigPagopa.pagamento_tipo == foreign(PagamentoTipo.id)"
    )
    importo_def: Mapped[ImportoTipo | None] = relationship(
        "ImportoTipo",
        lazy="joined",
        viewonly=True,
        primaryjoin="ConfigPagopa.importo_tipo == foreign(ImportoTipo.id)"
    )
