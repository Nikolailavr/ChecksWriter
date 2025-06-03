from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Receipt, ReceiptItem
from core.database.schemas import ReceiptSchema


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, receipt_data: ReceiptSchema) -> Receipt:
        try:
            receipt = Receipt(**receipt_data.model_dump())

            items = []
            for idx, item_data in enumerate(receipt_data.items):
                item = ReceiptItem(
                    unit=item_data.unit,
                    name=item_data.name,
                    price=item_data.price,
                    quantity=item_data.quantity,
                    sum=item_data.sum,
                    nds=item_data.nds,
                    product_type=item_data.productType,
                    payment_type=item_data.paymentType,
                    position=idx + 1,
                )
                items.append(item)

            receipt.items = items
            self.session.add(receipt)
            await self.session.commit()
            await self.session.refresh(receipt)
            return receipt

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e