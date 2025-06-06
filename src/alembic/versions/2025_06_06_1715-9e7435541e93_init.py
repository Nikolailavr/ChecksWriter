"""init

Revision ID: 9e7435541e93
Revises:
Create Date: 2025-06-06 17:15:48.199845

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e7435541e93"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("phone", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("telegram_id", name=op.f("pk_users")),
    )
    op.create_table(
        "receipts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("receipt_id", sa.String(length=20), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("code", sa.Integer(), nullable=False),
        sa.Column(
            "message_fiscal_sign",
            sa.Numeric(precision=20, scale=0),
            nullable=False,
        ),
        sa.Column("fiscal_drive_number", sa.String(length=16), nullable=False),
        sa.Column("kkt_reg_id", sa.String(length=20), nullable=False),
        sa.Column("user_inn", sa.String(length=12), nullable=False),
        sa.Column(
            "fiscal_document_number",
            sa.Numeric(precision=20, scale=0),
            nullable=False,
        ),
        sa.Column("date_time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column(
            "fiscal_sign", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column(
            "shift_number", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column(
            "request_number", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column(
            "operation_type", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column(
            "total_sum", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column(
            "fiscal_document_format_ver",
            sa.Numeric(precision=20, scale=0),
            nullable=False,
        ),
        sa.Column("buyer", sa.Text(), nullable=True),
        sa.Column("user", sa.String(), nullable=False),
        sa.Column("cash_total_sum", sa.BigInteger(), nullable=False),
        sa.Column("ecash_total_sum", sa.BigInteger(), nullable=False),
        sa.Column("prepaid_sum", sa.BigInteger(), nullable=False),
        sa.Column("credit_sum", sa.BigInteger(), nullable=False),
        sa.Column("provision_sum", sa.BigInteger(), nullable=False),
        sa.Column("nds_no", sa.Integer(), nullable=True),
        sa.Column("applied_taxation_type", sa.Integer(), nullable=True),
        sa.Column("operator", sa.Text(), nullable=True),
        sa.Column("operator_inn", sa.String(length=12), nullable=True),
        sa.Column("retail_place", sa.Text(), nullable=True),
        sa.Column("region", sa.String(length=10), nullable=True),
        sa.Column("number_kkt", sa.String(length=20), nullable=True),
        sa.Column(
            "redefine_mask", sa.Numeric(precision=20, scale=0), nullable=False
        ),
        sa.Column("ofd_id", sa.String(length=10), nullable=True),
        sa.Column("receive_date", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("subtype", sa.String(length=20), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default="now()",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.telegram_id"],
            name=op.f("fk_receipts_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_receipts")),
        sa.UniqueConstraint(
            "fiscal_drive_number",
            "fiscal_document_number",
            "fiscal_sign",
            name="unique_fiscal_data",
        ),
    )
    op.create_index(
        op.f("ix_receipts_receipt_id"), "receipts", ["receipt_id"], unique=True
    )
    op.create_table(
        "receipt_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("receipt_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column(
            "quantity", sa.Numeric(precision=10, scale=3), nullable=False
        ),
        sa.Column("sum", sa.BigInteger(), nullable=False),
        sa.Column("nds", sa.Integer(), nullable=True),
        sa.Column("product_type", sa.Integer(), nullable=True),
        sa.Column("payment_type", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["receipt_id"],
            ["receipts.receipt_id"],
            name=op.f("fk_receipt_items_receipt_id_receipts"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_receipt_items")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("receipt_items")
    op.drop_index(op.f("ix_receipts_receipt_id"), table_name="receipts")
    op.drop_table("receipts")
    op.drop_table("users")
    # ### end Alembic commands ###
