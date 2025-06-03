from core.database import db_helper
from core.database.DAL import ReceiptRepository
from core.database.schemas import ReceiptSchema


class ReceiptService:
    @staticmethod
    async def save_receipt(data: dict, telegram_id: int, category: str):
        async with db_helper.get_session() as session:
            receipt_data = ReceiptSchema.model_validate(data)
            receipt_data.user_id = telegram_id
            receipt_data.category = category
            receipt = await ReceiptRepository(session).create(receipt_data)
            return receipt
