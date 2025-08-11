from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class PagamentoTipo(Base):
    __tablename__ = "pagamento_tipo"
    __table_args__ = {"schema": "pagopa"}

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    descrizione: Mapped[str | None] = mapped_column(String, nullable=True)
