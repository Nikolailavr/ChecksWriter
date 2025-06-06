from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReceiptItemSchema(BaseModel):
    nds: Optional[int]
    sum: int
    name: str
    price: int
    quantity: float
    payment_type: Optional[int] = Field(None, alias="paymentType")
    product_type: Optional[int] = Field(None, alias="productType")

    class Config:
        orm_mode = True

class MetadataSchema(BaseModel):
    id: Optional[int] = None
    ofd_id: Optional[str] = Field(None, alias="ofdId")
    address: Optional[str] = None
    subtype: Optional[str] = None
    receive_date: Optional[datetime] = Field(None, alias="receiveDate")

class ReceiptSchema(BaseModel):
    user_id: Optional[int] = Field(None, alias="user_id")
    category: Optional[str] = None
    code: Optional[int] = None
    user: Optional[str] = None
    buyer: Optional[str] = None
    items: List[ReceiptItemSchema]
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
    user_id: Optional[int] = Field(None, alias="user_id")
    category: Optional[str] = None
    receipt_id: Optional[str] = None
    address: Optional[str] = None
    receive_date: Optional[datetime] = Field(None, alias="receiveDate")
    items: List[ReceiptItemSchema]
    date_time: datetime = Field(..., alias="dateTime")
    total_sum: int = Field(..., alias="totalSum")
    credit_sum: Optional[int] = Field(0, alias="creditSum")
    prepaid_sum: Optional[int] = Field(0, alias="prepaidSum")
    retail_place: Optional[str] = Field(None, alias="retailPlace")
    cash_total_sum: Optional[int] = Field(0, alias="cashTotalSum")
    provision_sum: Optional[int] = Field(0, alias="provisionSum")
    ecash_total_sum: Optional[int] = Field(0, alias="ecashTotalSum")

    class Config:
        orm_mode = True