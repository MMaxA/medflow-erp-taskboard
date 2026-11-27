from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Integer, Float, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
def now(): return datetime.now(timezone.utc)
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    full_name:Mapped[str]=mapped_column(String(180))
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[str]=mapped_column(String(40),default="project_manager")
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Project(Base):
    __tablename__="projects"
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    code:Mapped[str]=mapped_column(String(30),unique=True,index=True)
    name:Mapped[str]=mapped_column(String(250))
    customer:Mapped[str]=mapped_column(String(250))
    product:Mapped[str]=mapped_column(String(250),default="")
    stage:Mapped[str]=mapped_column(String(80),default="КП и подбор")
    owner:Mapped[str]=mapped_column(String(150),default="")
    owner_id:Mapped[int | None]=mapped_column(ForeignKey("users.id"),nullable=True,index=True)
    amount:Mapped[Decimal]=mapped_column(Numeric(14,2),default=Decimal("0.00"))
    probability:Mapped[int]=mapped_column(Integer,default=0)
    description:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class Task(Base):
    __tablename__="tasks"
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    code:Mapped[str]=mapped_column(String(30),unique=True,index=True)
    title:Mapped[str]=mapped_column(String(250))
    project_code:Mapped[str]=mapped_column(String(30),default="")
    assignee:Mapped[str]=mapped_column(String(150),default="")
    assignee_id:Mapped[int | None]=mapped_column(ForeignKey("users.id"),nullable=True,index=True)
    due_date:Mapped[str]=mapped_column(String(20),default="")
    status:Mapped[str]=mapped_column(String(50),default="Новая")
    priority:Mapped[str]=mapped_column(String(30),default="Средний")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class Activity(Base):
    __tablename__="activities"
    id:Mapped[int]=mapped_column(primary_key=True)
    project_code:Mapped[str]=mapped_column(String(30),index=True)
    actor:Mapped[str]=mapped_column(String(180))
    action:Mapped[str]=mapped_column(String(120))
    details:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Notification(Base):
    __tablename__="notifications"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    title:Mapped[str]=mapped_column(String(200))
    message:Mapped[str]=mapped_column(Text)
    is_read:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)


class Counterparty(Base):
    __tablename__ = "counterparties"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), index=True)
    kind: Mapped[str] = mapped_column(String(20), default="customer")  # customer, supplier, both
    tax_id: Mapped[str] = mapped_column(String(40), default="")
    registration_id: Mapped[str] = mapped_column(String(60), default="")
    contact_person: Mapped[str] = mapped_column(String(180), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(60), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_code: Mapped[str] = mapped_column(String(30), index=True)
    direction: Mapped[str] = mapped_column(String(20))  # incoming / outgoing
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    planned_date: Mapped[str] = mapped_column(String(10), default="")
    paid_date: Mapped[str] = mapped_column(String(10), default="")
    status: Mapped[str] = mapped_column(String(20), default="planned")  # planned / paid / cancelled
    reference: Mapped[str] = mapped_column(String(120), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(String(180))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

# CRM / commercial opportunities
class Contact(Base):
    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    counterparty_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(180))
    position: Mapped[str] = mapped_column(String(180), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    phone: Mapped[str] = mapped_column(String(60), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    manufacturer_id: Mapped[int | None] = mapped_column(ForeignKey("counterparties.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(250), index=True)
    model: Mapped[str] = mapped_column(String(180), default="")
    sku: Mapped[str] = mapped_column(String(100), default="")
    category: Mapped[str] = mapped_column(String(120), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    specifications: Mapped[str] = mapped_column(Text, default="")
    registration_docs: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Opportunity(Base):
    __tablename__ = "opportunities"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(250))
    customer_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stage: Mapped[str] = mapped_column(String(80), default="Новая потребность")
    description: Mapped[str] = mapped_column(Text, default="")
    budget: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    funding_status: Mapped[str] = mapped_column(String(80), default="Не уточнён")
    procurement_method: Mapped[str] = mapped_column(String(120), default="Не определена")
    expected_procurement_date: Mapped[str] = mapped_column(String(10), default="")
    probability: Mapped[int] = mapped_column(Integer, default=0)
    next_action: Mapped[str] = mapped_column(String(250), default="")
    next_action_date: Mapped[str] = mapped_column(String(10), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class OpportunityItem(Base):
    __tablename__ = "opportunity_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(250))
    model: Mapped[str] = mapped_column(String(180), default="")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    notes: Mapped[str] = mapped_column(Text, default="")

class CommercialOffer(Base):
    __tablename__ = "commercial_offers"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("counterparties.id"), index=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    discount_percent: Mapped[float] = mapped_column(Float, default=0)
    payment_terms: Mapped[str] = mapped_column(Text, default="")
    production_days: Mapped[int] = mapped_column(Integer, default=0)
    delivery_days: Mapped[int] = mapped_column(Integer, default=0)
    valid_until: Mapped[str] = mapped_column(String(10), default="")
    document_ref: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class CostLine(Base):
    __tablename__ = "cost_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(ForeignKey("opportunities.id", ondelete="CASCADE"), index=True)
    offer_id: Mapped[int | None] = mapped_column(ForeignKey("commercial_offers.id", ondelete="CASCADE"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(250), default="")
    amount: Mapped[Decimal] = mapped_column(Numeric(14,2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
