import asyncio
from typing import Sequence

from core.database import db_helper
from core.database.DAL import ReceiptRepository
from core.database.models import Receipt, ReceiptItem
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
    async def get_categories(telegram_id: int) -> list[Receipt]:
        async with db_helper.get_session() as session:
            categories = await ReceiptRepository(session).get(telegram_id)
            return categories

    @staticmethod
    async def get_receipts(telegram_id: int, category: str) -> list[Receipt]:
        async with db_helper.get_session() as session:
            receipts = await ReceiptRepository(session).get(telegram_id, category)
            return receipts

    @staticmethod
    async def get_receipt(receipt_id: str) -> Receipt:
        async with db_helper.get_session() as session:
            receipt = await ReceiptRepository(session).get_receipt(receipt_id)
            return receipt

    @staticmethod
    async def delete_receipt(receipt_id: str):
        async with db_helper.get_session() as session:
            return await ReceiptRepository(session).delete_receipt(receipt_id)

    @staticmethod
    async def update_category(receipt_id: str, new_category: str):
        async with db_helper.get_session() as session:
            await ReceiptRepository(session).update_category(receipt_id, new_category)
