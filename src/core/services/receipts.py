from sqlalchemy.ext.asyncio import AsyncSession


class ReceiptService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_receipt(self, data: dict): ...
