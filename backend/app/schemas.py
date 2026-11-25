from datetime import datetime
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
    product:str=""; stage:str="КП и подбор"; owner:str=""; amount:float=0
    probability:int=Field(default=0,ge=0,le=100); description:str=""
class ProjectOut(ProjectIn):
    id:int; created_at:datetime; updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
class TaskIn(BaseModel):
    code:str; title:str; project_code:str=""; assignee:str=""
    due_date:str=""; status:str="Новая"; priority:str="Средний"
class TaskOut(TaskIn):
    id:int; created_at:datetime; updated_at:datetime
    model_config=ConfigDict(from_attributes=True)
class TaskStatusIn(BaseModel): status:str
class TaskUpdate(BaseModel):
    title:str=Field(min_length=2,max_length=250); project_code:str=""; assignee:str=""
    due_date:str=""; status:str="Новая"; priority:str="Средний"
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
    amount: float = Field(gt=0, le=999999999999.99)
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
    code: str = Field(min_length=2, max_length=30); title: str = Field(min_length=2, max_length=250); customer_id: int; contact_id: int | None = None; owner_id: int; stage: str = "Новая потребность"; description: str = ""; budget: float = Field(default=0, ge=0); currency: str = "RUB"; funding_status: str = "Не уточнён"; procurement_method: str = "Не определена"; expected_procurement_date: str = ""; probability: int = Field(default=0, ge=0, le=100); next_action: str = ""; next_action_date: str = ""
class OpportunityOut(OpportunityIn):
    id: int; created_at: datetime; updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
class OpportunityItemIn(BaseModel):
    equipment_id: int | None = None; name: str = Field(min_length=2); model: str = ""; quantity: int = Field(default=1, ge=1); notes: str = ""
class OpportunityItemOut(OpportunityItemIn):
    id: int; opportunity_id: int
    model_config = ConfigDict(from_attributes=True)
class OfferIn(BaseModel):
    opportunity_id: int; supplier_id: int; equipment_id: int | None = None; description: str = ""; quantity: int = Field(default=1, ge=1); unit_price: float = Field(default=0, ge=0, le=999999999999.99); currency: str = "RUB"; discount_percent: float = Field(default=0, ge=0, le=100); payment_terms: str = ""; production_days: int = Field(default=0, ge=0); delivery_days: int = Field(default=0, ge=0); valid_until: str = ""; document_ref: str = ""
class OfferOut(OfferIn):
    id: int; created_at: datetime
    model_config = ConfigDict(from_attributes=True)
class CostLineIn(BaseModel):
    offer_id: int | None = None
    category: str = Field(min_length=2, max_length=80); description: str = ""; amount: float = Field(default=0, ge=0, le=999999999999.99); currency: str = "RUB"
class CostLineOut(CostLineIn):
    id: int; opportunity_id: int
    model_config = ConfigDict(from_attributes=True)
