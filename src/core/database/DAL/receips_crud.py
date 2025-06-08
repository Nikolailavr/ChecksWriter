from collections.abc import Sequence

from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.database.models import Receipt, ReceiptItem
from core.database.schemas import ReceiptSchema


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, receipt_schema: ReceiptSchema) -> Receipt:
        try:
            receipt = Receipt(
                receipt_id=str(receipt_schema.metadata.id),
                user_id=receipt_schema.user_id,
                category=receipt_schema.category,
                code=receipt_schema.code,
                message_fiscal_sign=receipt_schema.message_fiscal_sign,
                fiscal_drive_number=receipt_schema.fiscal_drive_number,
                kkt_reg_id=receipt_schema.kkt_reg_id.strip(),
                user_inn=receipt_schema.user_inn,
                fiscal_document_number=receipt_schema.fiscal_document_number,
                date_time=receipt_schema.date_time,
                fiscal_sign=receipt_schema.fiscal_sign,
                shift_number=receipt_schema.shift_number,
                request_number=receipt_schema.request_number,
                operation_type=receipt_schema.operation_type,
                total_sum=receipt_schema.total_sum,
                fiscal_document_format_ver=receipt_schema.fiscal_document_format_ver,
                buyer=receipt_schema.buyer,
                user=receipt_schema.user,
                cash_total_sum=receipt_schema.cash_total_sum,
                ecash_total_sum=receipt_schema.ecash_total_sum,
                prepaid_sum=receipt_schema.prepaid_sum,
                credit_sum=receipt_schema.credit_sum,
                provision_sum=receipt_schema.provision_sum,
                nds_no=receipt_schema.nds_no,
                applied_taxation_type=receipt_schema.applied_taxation_type,
                operator=receipt_schema.operator,
                operator_inn=receipt_schema.operator_inn,
                retail_place=receipt_schema.retail_place,
                region=receipt_schema.region,
                number_kkt=receipt_schema.number_kkt,
                redefine_mask=receipt_schema.redefine_mask,
                ofd_id=receipt_schema.metadata.ofd_id,
                receive_date=receipt_schema.metadata.receive_date,
                subtype=receipt_schema.metadata.subtype,
                address=receipt_schema.metadata.address,
            )
            # Добавляем все items
            receipt.items = []
            for pos, item in enumerate(receipt_schema.items, 1):
                receipt_item = ReceiptItem(
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity,
                    sum=item.sum,
                    nds=item.nds,
                    product_type=item.product_type,
                    payment_type=item.payment_type,
                    position=pos,
                )
                receipt.items.append(receipt_item)

            self.session.add(receipt)
            await self.session.commit()
            await self.session.refresh(receipt)
            return receipt

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get(
        self, telegram_id: int, category: str = None
    ) -> list[Receipt] | list[str]:
        try:
            if category:
                stmt = (
                    select(Receipt)
                    .options(joinedload(Receipt.items))
                    .where(Receipt.user_id == telegram_id, Receipt.category == category)
                    .order_by(Receipt.date_time.desc())
                )
                result = await self.session.execute(stmt)
                result = result.unique().scalars().all()
            else:
                stmt = (
                    select(Receipt.category)
                    .where(Receipt.user_id == telegram_id)
                    .distinct()
                )
                result = await self.session.execute(stmt)
                result = [row[0] for row in result.fetchall() if row[0]]
            return result
        except SQLAlchemyError as ex:
            raise ex

    async def get_receipt_items(self, receipt_id: str) -> Sequence[ReceiptItem]:
        try:
            stmt = select(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id)
            result = await self.session.execute(stmt)
            items = result.scalars().all()
            return items
        except SQLAlchemyError as ex:
            raise ex

    async def get_receipt(self, receipt_id: str) -> Receipt:
        try:
            stmt = (
                select(Receipt)
                .options(joinedload(Receipt.items))
                .where(Receipt.receipt_id == receipt_id)
            )
            result = await self.session.execute(stmt)
            return result.unique().scalar_one_or_none()
        except SQLAlchemyError as ex:
            raise ex

    async def delete_receipt(self, receipt_id: str) -> bool | None:
        try:
            await self.session.execute(
                delete(Receipt).where(Receipt.receipt_id == receipt_id)
            )
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def update_category(self, receipt_id: str, new_category: str):
        stmt = (
            update(Receipt)
            .where(Receipt.receipt_id == receipt_id)
            .values(category=new_category)
        )
        await self.session.execute(stmt)
        await self.session.commit()
