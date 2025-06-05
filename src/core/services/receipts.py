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

    @staticmethod
    async def get_categories(telegram_id: int):
        async with db_helper.get_session() as session:
            categories = await ReceiptRepository(session).get(telegram_id)
            return categories

    @staticmethod
    async def get_receipts(telegram_id: int, category: str):
        async with db_helper.get_session() as session:
            receipts = await ReceiptRepository(session).get(telegram_id, category)
            return receipts

    @staticmethod
    async def get_receipt(receipt_id: int):
        async with db_helper.get_session() as session:
            receipts = await ReceiptRepository(session).get_receipt(receipt_id)
            return receipts

    @staticmethod
    async def delete_receipt(receipt_id: int):
        async with db_helper.get_session() as session:
            return await ReceiptRepository(session).delete_receipt(receipt_id)
