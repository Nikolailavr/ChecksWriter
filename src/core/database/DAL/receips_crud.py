from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Receipt, ReceiptItem
from core.database.schemas import ReceiptSchema


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, receipt_schema: ReceiptSchema) -> Receipt:
        try:
            receipt = Receipt(
                user_id=receipt_schema.user_id,
                category=receipt_schema.category,
                code=receipt_schema.code,
                message_fiscal_sign=receipt_schema.messageFiscalSign,
                fiscal_drive_number=receipt_schema.fiscalDriveNumber,
                kkt_reg_id=receipt_schema.kktRegId.strip(),
                user_inn=receipt_schema.userInn,
                fiscal_document_number=receipt_schema.fiscalDocumentNumber,
                date_time=receipt_schema.dateTime,
                fiscal_sign=receipt_schema.fiscalSign,
                shift_number=receipt_schema.shiftNumber,
                request_number=receipt_schema.requestNumber,
                operation_type=receipt_schema.operationType,
                total_sum=receipt_schema.totalSum,
                fiscal_document_format_ver=receipt_schema.fiscalDocumentFormatVer,
                buyer=receipt_schema.buyer,
                cash_total_sum=receipt_schema.cashTotalSum,
                ecash_total_sum=receipt_schema.ecashTotalSum,
                prepaid_sum=receipt_schema.prepaidSum,
                credit_sum=receipt_schema.creditSum,
                provision_sum=receipt_schema.provisionSum,
                nds_no=receipt_schema.ndsNo,
                applied_taxation_type=receipt_schema.appliedTaxationType,
                operator=receipt_schema.operator,
                operator_inn=receipt_schema.operatorInn,
                retail_place=receipt_schema.retailPlace,
                region=receipt_schema.region,
                number_kkt=receipt_schema.numberKkt,
                redefine_mask=receipt_schema.redefine_mask,
                metadata_id=receipt_schema.metadata.id,
                ofd_id=receipt_schema.metadata.ofdId,
                receive_date=receipt_schema.metadata.receiveDate,
                subtype=receipt_schema.metadata.subtype,
                address=receipt_schema.metadata.address,
            )
            # Добавляем все items
            receipt.items = []
            for pos, item in enumerate(receipt_schema.items, 1):
                receipt_item = ReceiptItem(
                    unit=item.unit,
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity,
                    sum=item.sum,
                    nds=item.nds,
                    product_type=item.productType,
                    payment_type=item.paymentType,
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
