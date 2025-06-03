from core.database import db_helper
from core.database.DAL import ReceiptRepository
from core.database.schemas import ReceiptSchema
from core.database.schemas.receipts import MetadataSchema, ReceiptItemSchema


class ReceiptService:
    @staticmethod
    async def save_receipt(data: dict, telegram_id: int, category: str):
        async with db_helper.get_session() as session:
            # receipt_data = ReceiptSchema(
            #     user_id=telegram_id,
            #     category=category,
            #     code=data.get("code", 0),
            #     user=data.get("user", ""),
            #     buyer=data.get("buyer", ""),
            #     ndsNo=data.get("ndsNo", 0),
            #     region=data.get("region", ""),
            #     userInn=data.get("userInn", ""),
            #     dateTime=data.get("dateTime"),
            #     kktRegId=data.get("kktRegId", ""),
            #     metadata=MetadataSchema(
            #         id=data.get("metadata", {}).get("id"),
            #         ofdId=data.get("metadata", {}).get("ofdId", ""),
            #         address=data.get("metadata", {}).get("address", ""),
            #         subtype=data.get("metadata", {}).get("subtype", ""),
            #         receiveDate=data.get("metadata", {}).get("receiveDate"),
            #     ),
            #     operator=data.get("operator", ""),
            #     totalSum=data.get("totalSum", 0),
            #     creditSum=data.get("creditSum", 0),
            #     numberKkt=data.get("numberKkt", ""),
            #     fiscalSign=data.get("fiscalSign", 0),
            #     prepaidSum=data.get("prepaidSum", 0),
            #     operatorInn=data.get("operatorInn", ""),
            #     retailPlace=data.get("retailPlace", ""),
            #     shiftNumber=data.get("shiftNumber", 0),
            #     cashTotalSum=data.get("cashTotalSum", 0),
            #     provisionSum=data.get("provisionSum", 0),
            #     ecashTotalSum=data.get("ecashTotalSum", 0),
            #     operationType=data.get("operationType", 0),
            #     redefine_mask=data.get("redefine_mask", 0),
            #     requestNumber=data.get("requestNumber", 0),
            #     fiscalDriveNumber=data.get("fiscalDriveNumber", ""),
            #     messageFiscalSign=data.get("messageFiscalSign", 0),
            #     appliedTaxationType=data.get("appliedTaxationType", 0),
            #     fiscalDocumentNumber=data.get("fiscalDocumentNumber", 0),
            #     fiscalDocumentFormatVer=data.get("fiscalDocumentFormatVer", 0),
            #     items=[
            #         ReceiptItemSchema(
            #             nds=item.get("nds"),
            #             sum=item.get("sum"),
            #             name=item.get("name"),
            #             unit=item.get("unit"),
            #             price=item.get("price"),
            #             quantity=item.get("quantity"),
            #             paymentType=item.get("paymentType"),
            #             productType=item.get("productType"),
            #         )
            #         for item in data.get("items", {})
            #     ],
            # )
            receipt_data = ReceiptSchema.model_validate(data)
            receipt_data.user_id = telegram_id
            receipt_data.category = category
            receipt = await ReceiptRepository(session).create(receipt_data)
            return receipt
