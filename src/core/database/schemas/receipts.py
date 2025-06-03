from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ReceiptItemSchema(BaseModel):
    nds: Optional[int]
    sum: int
    name: str
    unit: str
    price: int
    quantity: float
    paymentType: Optional[int]
    productType: Optional[int]


class MetadataSchema(BaseModel):
    id: Optional[int]
    ofdId: Optional[str]
    address: Optional[str]
    subtype: Optional[str]
    receiveDate: Optional[datetime]


class ReceiptSchema(BaseModel):
    code: Optional[int]
    user_id: Optional[int]
    buyer: Optional[str]
    items: List[ReceiptItemSchema]
    ndsNo: Optional[int]
    region: Optional[str]
    userInn: str
    dateTime: datetime
    kktRegId: str
    metadata: Optional[MetadataSchema]
    operator: Optional[str]
    totalSum: int
    creditSum: Optional[int]
    numberKkt: Optional[str]
    fiscalSign: int
    prepaidSum: Optional[int]
    operatorInn: Optional[str]
    retailPlace: Optional[str]
    shiftNumber: int
    cashTotalSum: Optional[int]
    provisionSum: Optional[int]
    ecashTotalSum: Optional[int]
    operationType: int
    redefine_mask: Optional[int]
    requestNumber: int
    fiscalDriveNumber: str
    messageFiscalSign: int
    appliedTaxationType: Optional[int]
    fiscalDocumentNumber: int
    fiscalDocumentFormatVer: int
