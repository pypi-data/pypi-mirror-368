from datetime import date, datetime
from uuid import UUID
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Boolean, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseUUIDModel
from .pagamento_tipo import PagamentoTipo
from .importo import Importo


class Pagamento(BaseUUIDModel):
    __tablename__ = "pagamento"
    __table_args__ = {"schema": "pagopa"}

    document_id: Mapped[UUID] = mapped_column(nullable=False)
    parent_id: Mapped[UUID | None]
    tipo_id: Mapped[str] = mapped_column(ForeignKey("pagopa.pagamento_tipo.id"), nullable=False, default="VARIE")

    idpos: Mapped[str | None]
    iddeb: Mapped[str | None]
    iuv: Mapped[str | None]
    modello: Mapped[str | None]
    servizio: Mapped[str | None]
    importo: Mapped[float | None]
    pagato: Mapped[float | None]
    causale: Mapped[str | None]
    data_inizio: Mapped[date | None]
    data_scadenza: Mapped[date | None]
    data_scadenza_avviso: Mapped[date | None]
    tipo_scadenza: Mapped[str | None]
    testo_scadenza: Mapped[str | None]
    gg_scadenza: Mapped[int | None]

    data_pagamento: Mapped[date | None]
    ora_pagamento: Mapped[str | None]
    attestante: Mapped[str | None]
    data_inserimento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    stato: Mapped[str | None]
    esito: Mapped[str | None]
    accertamento: Mapped[str | None]
    gruppo: Mapped[str | None]
    ordinamento: Mapped[int | None]
    rata: Mapped[int | None]
    tassonomia: Mapped[str | None]

    soggetto: Mapped[str | None]
    cf_piva: Mapped[str | None]
    nome: Mapped[str | None]
    cognome: Mapped[str | None]
    denominazione: Mapped[str | None]
    indirizzo: Mapped[str | None]
    civico: Mapped[str | None]
    cap: Mapped[str | None]
    loc: Mapped[str | None]
    prov: Mapped[str | None]
    nazione: Mapped[str | None]
    email: Mapped[str | None]
    azione: Mapped[str | None]
    info: Mapped[str | None]

    readers: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_by_id: Mapped[str | None]
    created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[str | None]
    removed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    tipo_pagamento: Mapped[PagamentoTipo] = relationship(
        lazy="joined",
        primaryjoin="Pagamento.tipo_id == foreign(PagamentoTipo.id)"
    )

    importi: Mapped[list[Importo]] = relationship(
        back_populates="pagamento",
        lazy="selectin",
        primaryjoin="Pagamento.id == foreign(Importo.pagamento_id)",
        order_by="Importo.prog"
    )
