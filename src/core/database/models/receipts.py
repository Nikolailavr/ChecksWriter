from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    UniqueConstraint,
    BigInteger,
    Integer,
    String,
    TIMESTAMP,
    Text,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base

if TYPE_CHECKING:
    from .users import User


class Receipt(Base):
    __table_args__ = (
        UniqueConstraint(
            "fiscal_drive_number",
            "fiscal_document_number",
            "fiscal_sign",
            name="unique_fiscal_data",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    receipt_id: Mapped[int] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.telegram_id"),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String, nullable=True)
    code: Mapped[int] = mapped_column(Integer, nullable=False)
    message_fiscal_sign: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    fiscal_drive_number: Mapped[str] = mapped_column(String(16), nullable=False)
    kkt_reg_id: Mapped[str] = mapped_column(String(20), nullable=False)
    user_inn: Mapped[str] = mapped_column(String(12), nullable=False)
    fiscal_document_number: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    date_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    fiscal_sign: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    shift_number: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    request_number: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    operation_type: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    total_sum: Mapped[int] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    fiscal_document_format_ver: Mapped[int] = mapped_column(
        Numeric(20, 0), nullable=False
    )
    buyer: Mapped[Optional[str]] = mapped_column(Text)
    user: Mapped[str] = mapped_column(String)
    cash_total_sum: Mapped[int] = mapped_column(BigInteger, default=0)
    ecash_total_sum: Mapped[int] = mapped_column(BigInteger, default=0)
    prepaid_sum: Mapped[int] = mapped_column(BigInteger, default=0)
    credit_sum: Mapped[int] = mapped_column(BigInteger, default=0)
    provision_sum: Mapped[int] = mapped_column(BigInteger, default=0)
    nds_no: Mapped[Optional[int]] = mapped_column(Integer)
    applied_taxation_type: Mapped[Optional[int]] = mapped_column(Integer)
    operator: Mapped[Optional[str]] = mapped_column(Text)
    operator_inn: Mapped[Optional[str]] = mapped_column(String(12))
    retail_place: Mapped[Optional[str]] = mapped_column(Text)
    region: Mapped[Optional[str]] = mapped_column(String(10))
    number_kkt: Mapped[Optional[str]] = mapped_column(String(20))
    redefine_mask: Mapped[Optional[int]] = mapped_column(
        Numeric(20, 0),
        nullable=False,
    )
    ofd_id: Mapped[Optional[str]] = mapped_column(String(10))
    receive_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True))
    subtype: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default="now()"
    )
    items: Mapped[List["ReceiptItem"]] = relationship(
        back_populates="receipt", cascade="all, delete-orphan"
    )
    user_rel: Mapped["User"] = relationship(back_populates="receipts")


class ReceiptItem(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    receipt_id: Mapped[int] = mapped_column(
        String(20),
        ForeignKey("receipts.receipt_id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    sum: Mapped[int] = mapped_column(BigInteger, nullable=False)
    nds: Mapped[Optional[int]] = mapped_column(Integer)
    product_type: Mapped[Optional[int]] = mapped_column(Integer)
    payment_type: Mapped[Optional[int]] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    receipt: Mapped["Receipt"] = relationship(back_populates="items")
