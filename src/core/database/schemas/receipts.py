from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import re


class ReceiptItemSchema(BaseModel):
    nds: Optional[int] = Field(0)
    sum: int = Field(0)
    name: str = Field("-")
    price: int = Field(0)
    quantity: float = Field(0)
    payment_type: Optional[int] = Field(None, alias="paymentType")
    product_type: Optional[int] = Field(None, alias="productType")


class MetadataSchema(BaseModel):
    id: Optional[int] = None
    ofd_id: Optional[str] = Field(None, alias="ofdId")
    address: Optional[str] = None
    subtype: Optional[str] = None
    receive_date: Optional[datetime] = Field(None, alias="receiveDate")
    
    @validator('address')
    def clean_address(cls, v):
        if v is None:
            return v
        # Заменяем повторяющиеся запятые на одну
        cleaned = re.sub(r',+', ',', v)
        # Убираем запятые в начале и в конце строки
        cleaned = cleaned.strip(',')
        return cleaned


class ReceiptSchema(BaseModel):
    user_id: Optional[int] = Field(None, alias="user_id")
    category: Optional[str] = None
    code: Optional[int] = None
    user: Optional[str] = None
    buyer: Optional[str] = None
    items: List[ReceiptItemSchema]
    metadata: Optional[MetadataSchema] = None
    nds_no: Optional[int] = Field(None, alias="ndsNo")
    region: Optional[str] = None
    user_inn: str = Field(..., alias="userInn")
    date_time: datetime = Field(..., alias="dateTime")
    kkt_reg_id: str = Field(..., alias="kktRegId")
    operator: Optional[str] = None
    total_sum: int = Field(..., alias="totalSum")
    credit_sum: Optional[int] = Field(0, alias="creditSum")
    number_kkt: Optional[str] = Field(None, alias="numberKkt")
    fiscal_sign: int = Field(..., alias="fiscalSign")
    prepaid_sum: Optional[int] = Field(0, alias="prepaidSum")
    operator_inn: Optional[str] = Field(None, alias="operatorInn")
    retail_place: Optional[str] = Field(None, alias="retailPlace")
    shift_number: int = Field(..., alias="shiftNumber")
    cash_total_sum: Optional[int] = Field(0, alias="cashTotalSum")
    provision_sum: Optional[int] = Field(0, alias="provisionSum")
    ecash_total_sum: Optional[int] = Field(0, alias="ecashTotalSum")
    operation_type: int = Field(..., alias="operationType")
    redefine_mask: Optional[int] = Field(None, alias="redefine_mask")
    request_number: int = Field(..., alias="requestNumber")
    fiscal_drive_number: str = Field(..., alias="fiscalDriveNumber")
    message_fiscal_sign: int = Field(..., alias="messageFiscalSign")
    applied_taxation_type: Optional[int] = Field(None, alias="appliedTaxationType")
    fiscal_document_number: int = Field(..., alias="fiscalDocumentNumber")
    fiscal_document_format_ver: int = Field(..., alias="fiscalDocumentFormatVer")


class ReceiptDBSchema(BaseModel):
    user_id: int = None
    category: str = None
    receipt_id: str = None
    address: Optional[str] = None
    receive_date: Optional[datetime] = None
    items: List[ReceiptItemSchema]
    date_time: datetime
    total_sum: int = 0
    credit_sum: Optional[int] = 0
    prepaid_sum: Optional[int] = 0
    retail_place: Optional[str] = None
    cash_total_sum: Optional[int] = 0
    provision_sum: Optional[int] = 0
    ecash_total_sum: Optional[int] = 0
