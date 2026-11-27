from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field
class LoginIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=1,max_length=128)
class UserOut(BaseModel):
    id:int; email:str; full_name:str; role:str
    model_config=ConfigDict(from_attributes=True)
class TokenOut(BaseModel):
    access_token:str; token_type:str="bearer"; user:UserOut
class ProjectIn(BaseModel):
    code:str=Field(min_length=2,max_length=30); name:str; customer:str
    product:str=""; stage:str="КП и подбор"; owner:str=""; owner_id:int | None=None; amount:Decimal=Field(default=Decimal("0"),ge=0,le=Decimal("999999999999.99"))
    probability:int=Field(default=0,ge=0,le=100); description:str=""
class ProjectOut(ProjectIn):
    id:int; created_at:datetime; updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
class TaskIn(BaseModel):
    code:str; title:str; project_code:str=""; assignee:str=""; assignee_id:int | None=None
    due_date:str=""; status:Literal["Новая","В работе","На проверке","Выполнена"]= "Новая"; priority:Literal["Низкий","Средний","Высокий","Критический"]="Средний"
class TaskOut(TaskIn):
    id:int; created_at:datetime; updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
class TaskStatusIn(BaseModel): status:Literal["Новая","В работе","На проверке","Выполнена"]
class TaskUpdate(BaseModel):
    title:str=Field(min_length=2,max_length=250); project_code:str=""; assignee:str=""; assignee_id:int | None=None
    due_date:str=""; status:Literal["Новая","В работе","На проверке","Выполнена"]="Новая"; priority:Literal["Низкий","Средний","Высокий","Критический"]="Средний"
class NotificationOut(BaseModel):
    id:int; title:str; message:str; is_read:bool; created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class ActivityOut(BaseModel):
    id:int; project_code:str; actor:str; action:str; details:str; created_at:datetime
    model_config=ConfigDict(from_attributes=True)
class UserCreate(BaseModel):
    email:EmailStr; full_name:str; password:str=Field(min_length=10); role:str


class CounterpartyIn(BaseModel):
    name: str = Field(min_length=2, max_length=250)
    kind: str = Field(default="customer", pattern="^(customer|supplier|both)$")
    tax_id: str = ""
    registration_id: str = ""
    contact_person: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    notes: str = ""
    is_active: bool = True

class CounterpartyOut(CounterpartyIn):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaymentIn(BaseModel):
    project_code: str = Field(min_length=2, max_length=30)
    direction: str = Field(pattern="^(incoming|outgoing)$")
    amount: Decimal = Field(gt=0, le=Decimal("999999999999.99"), decimal_places=2)
    currency: str = Field(default="EUR", pattern="^(EUR|BGN|USD|RUB)$")
    planned_date: str = ""
    paid_date: str = ""
    status: str = Field(default="planned", pattern="^(planned|paid|cancelled)$")
    reference: str = ""
    description: str = ""

class PaymentOut(PaymentIn):
    id: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ContactIn(BaseModel):
    counterparty_id: int; full_name: str = Field(min_length=2, max_length=180); position: str = ""; email: str = ""; phone: str = ""; notes: str = ""
class ContactOut(ContactIn):
    id: int; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class EquipmentIn(BaseModel):
    manufacturer_id: int | None = None; name: str = Field(min_length=2, max_length=250); model: str = ""; sku: str = ""; category: str = ""; description: str = ""; specifications: str = ""; registration_docs: str = ""; is_active: bool = True
class EquipmentOut(EquipmentIn):
    id: int; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class OpportunityIn(BaseModel):
    code: str = Field(min_length=2, max_length=30); title: str = Field(min_length=2, max_length=250); customer_id: int; contact_id: int | None = None; owner_id: int; stage: str = "Новая потребность"; description: str = ""; budget: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999.99"), decimal_places=2); currency: str = Field(default="RUB", pattern="^(EUR|BGN|USD|RUB)$"); funding_status: str = "Не уточнён"; procurement_method: str = "Не определена"; expected_procurement_date: str = ""; probability: int = Field(default=0, ge=0, le=100); next_action: str = ""; next_action_date: str = ""
class OpportunityOut(OpportunityIn):
    id: int; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
class OpportunityItemIn(BaseModel):
    equipment_id: int | None = None; name: str = Field(min_length=2); model: str = ""; quantity: int = Field(default=1, ge=1, le=1000000); notes: str = ""
class OpportunityItemOut(OpportunityItemIn):
    id: int; opportunity_id: int
    model_config = ConfigDict(from_attributes=True)
class OfferIn(BaseModel):
    opportunity_id: int; supplier_id: int; equipment_id: int | None = None; description: str = ""; quantity: int = Field(default=1, ge=1, le=1000000); unit_price: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999.99"), decimal_places=2); currency: str = Field(default="RUB", pattern="^(EUR|BGN|USD|RUB)$"); discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100, decimal_places=2); payment_terms: str = ""; production_days: int = Field(default=0, ge=0, le=3650); delivery_days: int = Field(default=0, ge=0, le=3650); valid_until: str = ""; document_ref: str = ""
class OfferOut(OfferIn):
    id: int; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class CostLineIn(BaseModel):
    offer_id: int | None = None
    category: str = Field(min_length=2, max_length=80); description: str = ""; amount: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("999999999999.99"), decimal_places=2); currency: str = Field(default="RUB", pattern="^(EUR|BGN|USD|RUB)$")
class CostLineOut(CostLineIn):
    id: int; opportunity_id: int
    model_config = ConfigDict(from_attributes=True)
