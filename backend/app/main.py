from fastapi import FastAPI,Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import desc, inspect, text
from .database import Base,engine,get_db,SessionLocal
from . import models
from .models import User,Project,Task,Activity,Notification
from .schemas import LoginIn,TokenOut,UserOut,ProjectIn,ProjectOut,TaskIn,TaskOut,TaskStatusIn,TaskUpdate,NotificationOut,ActivityOut,UserCreate,CounterpartyIn,CounterpartyOut,PaymentIn,PaymentOut,ContactIn,ContactOut,EquipmentIn,EquipmentOut,OpportunityIn,OpportunityOut,OpportunityItemIn,OpportunityItemOut,OfferIn,OfferOut,CostLineIn,CostLineOut
from .security import verify_password,create_access_token,hash_password
from .deps import current_user,require_roles
from .config import settings
from .seed import seed
Base.metadata.create_all(bind=engine)
# Lightweight additive migration for databases created by Foundation 0.6.
with engine.begin() as conn:
    if "cost_lines" in inspect(engine).get_table_names():
        cols = {c["name"] for c in inspect(engine).get_columns("cost_lines")}
        if "offer_id" not in cols:
            conn.execute(text("ALTER TABLE cost_lines ADD COLUMN offer_id INTEGER NULL"))
with SessionLocal() as db: seed(db)
app=FastAPI(title="MedFlow ERP API",version="0.2.0",description="Foundation API: JWT, RBAC, projects, tasks, activity and notifications")
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.get("/api/health")
def health(): return {"status":"ok","service":"medflow-api","version":"0.2.0"}
@app.post("/api/auth/login",response_model=TokenOut)
def login(payload:LoginIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==payload.email).first()
    if not user or not verify_password(payload.password,user.password_hash): raise HTTPException(401,"Неверный email или пароль")
    if not user.is_active: raise HTTPException(403,"Пользователь заблокирован")
    return {"access_token":create_access_token(user.email),"user":user}
@app.get("/api/auth/me",response_model=UserOut)
def me(user:User=Depends(current_user)): return user
@app.get("/api/users",response_model=list[UserOut])
def users(db:Session=Depends(get_db),user:User=Depends(require_roles("admin","director"))):
    return db.query(User).order_by(User.id).all()
@app.post("/api/users",response_model=UserOut,status_code=201)
def create_user(payload:UserCreate,db:Session=Depends(get_db),user:User=Depends(require_roles("admin"))):
    allowed={"director","project_manager","accountant","lawyer","office_manager","admin"}
    if payload.role not in allowed: raise HTTPException(400,"Unknown role")
    if db.query(User).filter_by(email=payload.email).first(): raise HTTPException(409,"Email already exists")
    obj=User(email=payload.email,full_name=payload.full_name,role=payload.role,password_hash=hash_password(payload.password))
    db.add(obj);db.commit();db.refresh(obj);return obj
@app.get("/api/projects",response_model=list[ProjectOut])
def projects(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(Project).order_by(desc(Project.updated_at)).all()
@app.post("/api/projects",response_model=ProjectOut,status_code=201)
def create_project(payload:ProjectIn,db:Session=Depends(get_db),user:User=Depends(require_roles("admin","director","project_manager"))):
    if db.query(Project).filter_by(code=payload.code).first(): raise HTTPException(409,"Код проекта уже существует")
    obj=Project(**payload.model_dump());db.add(obj);db.flush()
    db.add(Activity(project_code=obj.code,actor=user.full_name,action="Создан проект",details=obj.name))
    for recipient in db.query(User).filter(User.is_active==True).all():
        if recipient.id != user.id: db.add(Notification(user_id=recipient.id,title="Создан новый проект",message=f"{user.full_name}: {obj.name}"))
    db.commit();db.refresh(obj);return obj
@app.get("/api/projects/{code}/activity",response_model=list[ActivityOut])
def project_activity(code:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(Activity).filter_by(project_code=code).order_by(desc(Activity.created_at)).all()
@app.patch("/api/projects/{code}",response_model=ProjectOut)
def update_project(code:str,payload:ProjectIn,db:Session=Depends(get_db),user:User=Depends(require_roles("admin","director","project_manager"))):
    obj=db.query(Project).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Проект не найден")
    before={"name":obj.name,"customer":obj.customer,"product":obj.product,"stage":obj.stage,"owner":obj.owner,"amount":obj.amount,"probability":obj.probability,"description":obj.description}
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    changes=[]
    for key,label in (("name","Название"),("customer","Заказчик"),("product","Оборудование"),("stage","Этап"),("owner","Ответственный"),("amount","Цена контракта"),("probability","Вероятность"),("description","Описание")):
        if before[key] != getattr(obj,key): changes.append(label)
    db.add(Activity(project_code=code,actor=user.full_name,action="Изменён проект",details="Изменены поля: " + (", ".join(changes) if changes else "без изменений")))
    db.commit();db.refresh(obj);return obj
@app.delete("/api/projects/{code}",status_code=204)
def delete_project(code:str,db:Session=Depends(get_db),user:User=Depends(require_roles("admin","director","project_manager"))):
    obj=db.query(Project).filter_by(code=code).first()
    if not obj: raise HTTPException(404,"Проект не найден")
    # Remove dependent records explicitly because the MVP schema does not yet define FK cascades.
    db.query(Task).filter(Task.project_code==code).delete(synchronize_session=False)
    db.query(Activity).filter(Activity.project_code==code).delete(synchronize_session=False)
    db.delete(obj);db.commit();return None
@app.get("/api/tasks",response_model=list[TaskOut])
def tasks(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(Task).order_by(desc(Task.created_at)).all()
@app.get("/api/task-assignees",response_model=list[UserOut])
def task_assignees(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(User).filter(User.is_active==True).order_by(User.full_name).all()
@app.post("/api/tasks",response_model=TaskOut,status_code=201)
def create_task(payload:TaskIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if db.query(Task).filter_by(code=payload.code).first(): raise HTTPException(409,"Код задачи уже существует")
    if payload.project_code and not db.query(Project).filter_by(code=payload.project_code).first(): raise HTTPException(404,"Указанный проект не найден")
    obj=Task(**payload.model_dump());db.add(obj);db.flush()
    if obj.project_code: db.add(Activity(project_code=obj.project_code,actor=user.full_name,action="Создана задача",details=f"{obj.code}: {obj.title}"))
    recipient=db.query(User).filter(User.full_name==obj.assignee,User.is_active==True).first()
    if recipient and recipient.id != user.id: db.add(Notification(user_id=recipient.id,title="Назначена новая задача",message=f"{obj.code}: {obj.title}"))
    db.commit();db.refresh(obj);return obj
@app.patch("/api/tasks/{task_id}",response_model=TaskOut)
def update_task(task_id:int,payload:TaskUpdate,db:Session=Depends(get_db),user:User=Depends(current_user)):
    obj=db.get(Task,task_id)
    if not obj: raise HTTPException(404,"Задача не найдена")
    managers={"admin","director","project_manager","office_manager"}
    if user.role not in managers and obj.assignee!=user.full_name: raise HTTPException(403,"Недостаточно прав")
    if payload.project_code and not db.query(Project).filter_by(code=payload.project_code).first(): raise HTTPException(404,"Указанный проект не найден")
    old_assignee=obj.assignee; old_status=obj.status; old_project=obj.project_code
    for key,value in payload.model_dump().items(): setattr(obj,key,value)
    if old_project and old_project != obj.project_code: db.add(Activity(project_code=old_project,actor=user.full_name,action="Изменена задача",details=f"{obj.code}: задача перенесена в другой проект"))
    if obj.project_code: db.add(Activity(project_code=obj.project_code,actor=user.full_name,action="Изменена задача",details=f"{obj.code}: {obj.title}"))
    recipient=db.query(User).filter(User.full_name==obj.assignee,User.is_active==True).first()
    if recipient and (obj.assignee!=old_assignee or obj.status!=old_status) and recipient.id!=user.id:
        db.add(Notification(user_id=recipient.id,title="Обновлена задача",message=f"{obj.code}: {obj.title}. Статус: {obj.status}"))
    db.commit();db.refresh(obj);return obj
@app.patch("/api/tasks/{task_id}/status",response_model=TaskOut)
def update_task_status(task_id:int,payload:TaskStatusIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    obj=db.get(Task,task_id)
    if not obj: raise HTTPException(404,"Задача не найдена")
    if user.role not in {"admin","director","project_manager","office_manager"} and obj.assignee!=user.full_name: raise HTTPException(403,"Недостаточно прав")
    previous=obj.status;obj.status=payload.status
    if obj.project_code: db.add(Activity(project_code=obj.project_code,actor=user.full_name,action="Изменён статус задачи",details=f"{obj.code}: {previous} → {obj.status}"))
    recipient=db.query(User).filter(User.full_name==obj.assignee,User.is_active==True).first()
    if recipient and recipient.id != user.id: db.add(Notification(user_id=recipient.id,title="Изменён статус задачи",message=f"{obj.title}: {previous} → {obj.status}"))
    db.commit();db.refresh(obj);return obj
@app.get("/api/notifications",response_model=list[NotificationOut])
def notifications(db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(desc(Notification.created_at)).all()
@app.patch("/api/notifications/{notification_id}/read")
def read_notification(notification_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    item=db.query(Notification).filter_by(id=notification_id,user_id=user.id).first()
    if not item: raise HTTPException(404,"Уведомление не найдено")
    item.is_read=True;db.commit();return {"ok":True}


# Trading: counterparties and cash-flow register
@app.get("/api/counterparties", response_model=list[CounterpartyOut])
def list_counterparties(kind: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    query = db.query(models.Counterparty)
    if kind in {"customer", "supplier"}:
        query = query.filter(models.Counterparty.kind.in_([kind, "both"]))
    return query.order_by(models.Counterparty.name).all()

@app.post("/api/counterparties", response_model=CounterpartyOut, status_code=201)
def create_counterparty(payload: CounterpartyIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "project_manager", "accountant", "office_manager"))):
    obj = models.Counterparty(**payload.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

@app.patch("/api/counterparties/{counterparty_id}", response_model=CounterpartyOut)
def update_counterparty(counterparty_id: int, payload: CounterpartyIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "project_manager", "accountant", "office_manager"))):
    obj = db.get(models.Counterparty, counterparty_id)
    if not obj: raise HTTPException(404, "Контрагент не найден")
    for key, value in payload.model_dump().items(): setattr(obj, key, value)
    db.commit(); db.refresh(obj)
    return obj

@app.get("/api/payments", response_model=list[PaymentOut])
def list_payments(project_code: str | None = None, status: str | None = None, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "accountant", "project_manager"))):
    query = db.query(models.Payment)
    if project_code: query = query.filter(models.Payment.project_code == project_code)
    if status in {"planned", "paid", "cancelled"}: query = query.filter(models.Payment.status == status)
    return query.order_by(models.Payment.planned_date, models.Payment.id).all()

@app.post("/api/payments", response_model=PaymentOut, status_code=201)
def create_payment(payload: PaymentIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "accountant"))):
    if not db.query(Project).filter_by(code=payload.project_code).first(): raise HTTPException(404, "Контракт не найден")
    data = payload.model_dump()
    if data["status"] == "paid" and not data["paid_date"]: raise HTTPException(422, "Для проведённого платежа укажите дату оплаты")
    obj = models.Payment(**data, created_by=user.full_name)
    db.add(obj)
    db.add(Activity(project_code=obj.project_code, actor=user.full_name, action="Добавлен платёж", details=f"{obj.direction}: {obj.amount} {obj.currency}"))
    db.commit(); db.refresh(obj)
    return obj

@app.patch("/api/payments/{payment_id}", response_model=PaymentOut)
def update_payment(payment_id: int, payload: PaymentIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "accountant"))):
    obj = db.get(models.Payment, payment_id)
    if not obj: raise HTTPException(404, "Платёж не найден")
    if not db.query(Project).filter_by(code=payload.project_code).first(): raise HTTPException(404, "Контракт не найден")
    data = payload.model_dump()
    if data["status"] == "paid" and not data["paid_date"]: raise HTTPException(422, "Для проведённого платежа укажите дату оплаты")
    for key, value in data.items(): setattr(obj, key, value)
    db.add(Activity(project_code=obj.project_code, actor=user.full_name, action="Изменён платёж", details=f"Платёж #{obj.id}: {obj.status}, {obj.amount} {obj.currency}"))
    db.commit(); db.refresh(obj)
    return obj

@app.get("/api/projects/{code}/financial-summary")
def project_financial_summary(code: str, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "accountant", "project_manager"))):
    project = db.query(Project).filter_by(code=code).first()
    if not project: raise HTTPException(404, "Контракт не найден")
    payments = db.query(models.Payment).filter_by(project_code=code).all()
    totals = {}
    for payment in payments:
        row = totals.setdefault(payment.currency, {"incoming_paid": 0.0, "outgoing_paid": 0.0, "incoming_planned": 0.0, "outgoing_planned": 0.0})
        if payment.status == "cancelled": continue
        suffix = "paid" if payment.status == "paid" else "planned"
        key = f"{payment.direction}_{suffix}"
        row[key] += float(payment.amount)
    return {"project_code": code, "contract_amount": project.amount, "payments_by_currency": totals, "payment_count": len(payments)}


# Foundation 0.6 — CRM and commercial opportunity management
CRM_EDIT_ROLES = ("admin", "director", "project_manager", "office_manager", "analyst")
OPPORTUNITY_STAGES = ("Новая потребность", "Первичный анализ", "Подбор оборудования", "Запрос коммерческих предложений", "Согласование решения с ЛПУ", "Ожидание финансирования", "Ожидание публикации закупки", "Передана в тендерную работу", "Отложена", "Закрыта без реализации")

def crm_audit(db, user, action, details):
    # Reuse the global activity stream; CRM events use a stable CRM namespace.
    db.add(Activity(project_code="CRM", actor=user.full_name, action=action, details=details))

@app.get("/api/crm/contacts", response_model=list[ContactOut])
def crm_contacts(counterparty_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(models.Contact)
    if counterparty_id: q = q.filter_by(counterparty_id=counterparty_id)
    return q.order_by(models.Contact.full_name).all()

@app.post("/api/crm/contacts", response_model=ContactOut, status_code=201)
def crm_create_contact(payload: ContactIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    if not db.get(models.Counterparty, payload.counterparty_id): raise HTTPException(404, "Контрагент не найден")
    obj=models.Contact(**payload.model_dump()); db.add(obj); crm_audit(db,user,"Добавлен контакт",payload.full_name); db.commit(); db.refresh(obj); return obj

@app.get("/api/crm/equipment", response_model=list[EquipmentOut])
def crm_equipment(search: str = "", db: Session = Depends(get_db), user: User = Depends(current_user)):
    q=db.query(models.Equipment)
    if search: q=q.filter(models.Equipment.name.ilike(f"%{search}%") | models.Equipment.model.ilike(f"%{search}%"))
    return q.order_by(models.Equipment.name).all()

@app.post("/api/crm/equipment", response_model=EquipmentOut, status_code=201)
def crm_create_equipment(payload: EquipmentIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    if payload.manufacturer_id and not db.get(models.Counterparty,payload.manufacturer_id): raise HTTPException(404,"Производитель не найден")
    obj=models.Equipment(**payload.model_dump()); db.add(obj); crm_audit(db,user,"Добавлено оборудование",f"{obj.name} {obj.model}"); db.commit(); db.refresh(obj); return obj

@app.patch("/api/crm/equipment/{item_id}", response_model=EquipmentOut)
def crm_update_equipment(item_id:int,payload:EquipmentIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    obj=db.get(models.Equipment,item_id)
    if not obj: raise HTTPException(404,"Оборудование не найдено")
    if payload.manufacturer_id and not db.get(models.Counterparty, payload.manufacturer_id): raise HTTPException(404, "Производитель не найден")
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    crm_audit(db,user,"Изменено оборудование",f"#{item_id}: {obj.name}"); db.commit(); db.refresh(obj); return obj

@app.get("/api/crm/opportunities", response_model=list[OpportunityOut])
def crm_opportunities(stage: str | None = None, customer_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    q=db.query(models.Opportunity)
    if stage: q=q.filter_by(stage=stage)
    if customer_id: q=q.filter_by(customer_id=customer_id)
    if user.role not in {"admin","director","project_manager","accountant","lawyer","office_manager","analyst"}: q=q.filter_by(owner_id=user.id)
    return q.order_by(models.Opportunity.updated_at.desc()).all()

@app.post("/api/crm/opportunities", response_model=OpportunityOut, status_code=201)
def crm_create_opportunity(payload:OpportunityIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    if db.query(models.Opportunity).filter_by(code=payload.code).first(): raise HTTPException(409,"Код возможности уже существует")
    customer=db.get(models.Counterparty,payload.customer_id)
    if not customer or customer.kind not in {"customer","both"}: raise HTTPException(422,"Выберите заказчика с типом customer или both")
    if payload.contact_id and not db.query(models.Contact).filter_by(id=payload.contact_id,counterparty_id=payload.customer_id).first(): raise HTTPException(422,"Контакт не принадлежит выбранному заказчику")
    if not db.get(User,payload.owner_id): raise HTTPException(404,"Ответственный пользователь не найден")
    obj=models.Opportunity(**payload.model_dump()); db.add(obj); crm_audit(db,user,"Создана коммерческая возможность",f"{obj.code}: {obj.title}"); db.commit(); db.refresh(obj); return obj

@app.patch("/api/crm/opportunities/{opp_id}", response_model=OpportunityOut)
def crm_update_opportunity(opp_id:int,payload:OpportunityIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    obj=db.get(models.Opportunity,opp_id)
    if not obj: raise HTTPException(404,"Коммерческая возможность не найдена")
    customer=db.get(models.Counterparty,payload.customer_id)
    if not customer or customer.kind not in {"customer","both"}: raise HTTPException(422,"Некорректный заказчик")
    if not db.get(User, payload.owner_id): raise HTTPException(404, "Ответственный пользователь не найден")
    if payload.contact_id and not db.query(models.Contact).filter_by(id=payload.contact_id,counterparty_id=payload.customer_id).first(): raise HTTPException(422,"Контакт не принадлежит выбранному заказчику")
    for k,v in payload.model_dump().items(): setattr(obj,k,v)
    crm_audit(db,user,"Изменена коммерческая возможность",f"{obj.code}: {obj.stage}"); db.commit(); db.refresh(obj); return obj

@app.get("/api/crm/opportunities/{opp_id}/items",response_model=list[OpportunityItemOut])
def crm_opportunity_items(opp_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if not db.get(models.Opportunity,opp_id): raise HTTPException(404,"Возможность не найдена")
    return db.query(models.OpportunityItem).filter_by(opportunity_id=opp_id).order_by(models.OpportunityItem.id).all()

@app.post("/api/crm/opportunities/{opp_id}/items",response_model=OpportunityItemOut,status_code=201)
def crm_add_opportunity_item(opp_id:int,payload:OpportunityItemIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    if not db.get(models.Opportunity,opp_id): raise HTTPException(404,"Возможность не найдена")
    if payload.equipment_id and not db.get(models.Equipment,payload.equipment_id): raise HTTPException(404,"Позиция каталога не найдена")
    obj=models.OpportunityItem(opportunity_id=opp_id,**payload.model_dump());db.add(obj);crm_audit(db,user,"Добавлена позиция потребности",payload.name);db.commit();db.refresh(obj);return obj

@app.delete("/api/crm/opportunities/{opp_id}/items/{item_id}",status_code=204)
def crm_delete_opportunity_item(opp_id:int,item_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    obj=db.query(models.OpportunityItem).filter_by(id=item_id,opportunity_id=opp_id).first()
    if not obj: raise HTTPException(404,"Позиция не найдена")
    db.delete(obj);db.commit();return None

@app.get("/api/crm/offers",response_model=list[OfferOut])
def crm_offers(opportunity_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    return db.query(models.CommercialOffer).filter_by(opportunity_id=opportunity_id).order_by(models.CommercialOffer.created_at.desc()).all()

@app.post("/api/crm/offers",response_model=OfferOut,status_code=201)
def crm_create_offer(payload:OfferIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    if not db.get(models.Opportunity,payload.opportunity_id): raise HTTPException(404,"Возможность не найдена")
    supplier=db.get(models.Counterparty,payload.supplier_id)
    if not supplier or supplier.kind not in {"supplier","both"}: raise HTTPException(422,"Выберите поставщика или производителя")
    if payload.equipment_id and not db.get(models.Equipment,payload.equipment_id): raise HTTPException(404,"Оборудование не найдено")
    obj=models.CommercialOffer(**payload.model_dump());db.add(obj);crm_audit(db,user,"Добавлено коммерческое предложение",f"Возможность #{obj.opportunity_id}, {obj.unit_price} {obj.currency}");db.commit();db.refresh(obj);return obj

@app.patch("/api/crm/offers/{offer_id}",response_model=OfferOut)
def crm_update_offer(offer_id:int,payload:OfferIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    obj=db.get(models.CommercialOffer,offer_id)
    if not obj: raise HTTPException(404,"КП не найдено")
    if payload.opportunity_id != obj.opportunity_id: raise HTTPException(422,"Нельзя переносить КП в другую возможность")
    supplier=db.get(models.Counterparty,payload.supplier_id)
    if not supplier or supplier.kind not in {"supplier","both"}: raise HTTPException(422,"Выберите поставщика или производителя")
    if payload.equipment_id and not db.get(models.Equipment,payload.equipment_id): raise HTTPException(404,"Оборудование не найдено")
    for key,value in payload.model_dump().items(): setattr(obj,key,value)
    crm_audit(db,user,"Изменено коммерческое предложение",f"КП #{offer_id}");db.commit();db.refresh(obj);return obj

@app.delete("/api/crm/offers/{offer_id}",status_code=204)
def crm_delete_offer(offer_id:int,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    obj=db.get(models.CommercialOffer,offer_id)
    if not obj: raise HTTPException(404,"КП не найдено")
    db.query(models.CostLine).filter_by(offer_id=offer_id).delete(synchronize_session=False)
    crm_audit(db,user,"Удалено коммерческое предложение",f"КП #{offer_id}");db.delete(obj);db.commit();return None

@app.get("/api/crm/opportunities/{opp_id}/costs",response_model=list[CostLineOut])
def crm_costs(opp_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if not db.get(models.Opportunity,opp_id): raise HTTPException(404,"Возможность не найдена")
    return db.query(models.CostLine).filter_by(opportunity_id=opp_id).order_by(models.CostLine.id).all()

@app.post("/api/crm/opportunities/{opp_id}/costs",response_model=CostLineOut,status_code=201)
def crm_add_cost(opp_id:int,payload:CostLineIn,db:Session=Depends(get_db),user:User=Depends(require_roles(*CRM_EDIT_ROLES))):
    if not db.get(models.Opportunity,opp_id): raise HTTPException(404,"Возможность не найдена")
    data=payload.model_dump(); offer_id=data.get("offer_id")
    if offer_id and not db.query(models.CommercialOffer).filter_by(id=offer_id,opportunity_id=opp_id).first(): raise HTTPException(404,"КП не найдено в этой возможности")
    obj=models.CostLine(opportunity_id=opp_id,**data);db.add(obj);crm_audit(db,user,"Добавлена статья затрат",f"{payload.category}: {payload.amount} {payload.currency}");db.commit();db.refresh(obj);return obj

@app.get("/api/crm/opportunities/{opp_id}/economics")
def crm_economics(opp_id:int, selling_price:float=0, currency:str="RUB", db:Session=Depends(get_db),user:User=Depends(current_user)):
    if not db.get(models.Opportunity,opp_id): raise HTTPException(404,"Возможность не найдена")
    offers=db.query(models.CommercialOffer).filter_by(opportunity_id=opp_id).all(); costs=db.query(models.CostLine).filter_by(opportunity_id=opp_id).all()
    currencies={currency} | {x.currency for x in offers} | {x.currency for x in costs}
    result={}
    for cur in currencies:
        offer_total=sum(float(x.unit_price)*x.quantity*(1-x.discount_percent/100) for x in offers if x.currency==cur)
        extra=sum(float(x.amount) for x in costs if x.currency==cur)
        sale=selling_price if cur==currency else 0
        total=offer_total+extra; profit=sale-total
        result[cur]={"equipment_cost":round(offer_total,2),"additional_costs":round(extra,2),"total_cost":round(total,2),"selling_price":round(sale,2),"gross_profit":round(profit,2),"gross_margin_percent":round(profit/sale*100,2) if sale else None}
    return {"opportunity_id":opp_id,"currencies":result,"note":"Суммы в разных валютах не конвертируются; сравнивайте отдельно до настройки курсов валют."}


# CRUD completion for CRM entities
@app.delete("/api/counterparties/{counterparty_id}", status_code=204)
def delete_counterparty(counterparty_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "project_manager", "office_manager"))):
    obj = db.get(models.Counterparty, counterparty_id)
    if not obj: raise HTTPException(404, "Контрагент не найден")
    linked = (
        db.query(models.Contact).filter_by(counterparty_id=counterparty_id).first()
        or db.query(models.Opportunity).filter_by(customer_id=counterparty_id).first()
        or db.query(models.Equipment).filter_by(manufacturer_id=counterparty_id).first()
        or db.query(models.CommercialOffer).filter_by(supplier_id=counterparty_id).first()
    )
    if linked: raise HTTPException(409, "Нельзя удалить контрагента: он используется в контактах, возможностях, оборудовании или КП. Сначала отвяжите связанные записи.")
    db.delete(obj); db.commit(); return None

@app.patch("/api/crm/contacts/{contact_id}", response_model=ContactOut)
def crm_update_contact(contact_id: int, payload: ContactIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.get(models.Contact, contact_id)
    if not obj: raise HTTPException(404, "Контакт не найден")
    if not db.get(models.Counterparty, payload.counterparty_id): raise HTTPException(404, "Контрагент не найден")
    for key, value in payload.model_dump().items(): setattr(obj, key, value)
    crm_audit(db, user, "Изменён контакт", f"#{contact_id}: {obj.full_name}")
    db.commit(); db.refresh(obj); return obj

@app.delete("/api/crm/contacts/{contact_id}", status_code=204)
def crm_delete_contact(contact_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.get(models.Contact, contact_id)
    if not obj: raise HTTPException(404, "Контакт не найден")
    if db.query(models.Opportunity).filter_by(contact_id=contact_id).first():
        raise HTTPException(409, "Контакт используется в коммерческой возможности. Сначала отвяжите его.")
    db.delete(obj); db.commit(); return None

@app.delete("/api/crm/equipment/{item_id}", status_code=204)
def crm_delete_equipment(item_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.get(models.Equipment, item_id)
    if not obj: raise HTTPException(404, "Оборудование не найдено")
    linked = db.query(models.OpportunityItem).filter_by(equipment_id=item_id).first() or db.query(models.CommercialOffer).filter_by(equipment_id=item_id).first()
    if linked: raise HTTPException(409, "Оборудование используется в возможностях или КП. Сначала отвяжите его.")
    db.delete(obj); db.commit(); return None

@app.delete("/api/crm/opportunities/{opp_id}", status_code=204)
def crm_delete_opportunity(opp_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.get(models.Opportunity, opp_id)
    if not obj: raise HTTPException(404, "Коммерческая возможность не найдена")
    db.query(models.CostLine).filter_by(opportunity_id=opp_id).delete(synchronize_session=False)
    db.query(models.CommercialOffer).filter_by(opportunity_id=opp_id).delete(synchronize_session=False)
    db.query(models.OpportunityItem).filter_by(opportunity_id=opp_id).delete(synchronize_session=False)
    crm_audit(db, user, "Удалена коммерческая возможность", f"{obj.code}: {obj.title}")
    db.delete(obj); db.commit(); return None

@app.patch("/api/crm/opportunities/{opp_id}/costs/{cost_id}", response_model=CostLineOut)
def crm_update_cost(opp_id: int, cost_id: int, payload: CostLineIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.query(models.CostLine).filter_by(id=cost_id, opportunity_id=opp_id).first()
    if not obj: raise HTTPException(404, "Статья затрат не найдена")
    if payload.offer_id and not db.query(models.CommercialOffer).filter_by(id=payload.offer_id, opportunity_id=opp_id).first():
        raise HTTPException(404, "КП не найдено в этой возможности")
    for key, value in payload.model_dump().items(): setattr(obj, key, value)
    crm_audit(db, user, "Изменена статья затрат", f"{payload.category}: {payload.amount} {payload.currency}")
    db.commit(); db.refresh(obj); return obj

@app.delete("/api/crm/opportunities/{opp_id}/costs/{cost_id}", status_code=204)
def crm_delete_cost(opp_id: int, cost_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.query(models.CostLine).filter_by(id=cost_id, opportunity_id=opp_id).first()
    if not obj: raise HTTPException(404, "Статья затрат не найдена")
    db.delete(obj); db.commit(); return None

@app.delete("/api/payments/{payment_id}", status_code=204)
def delete_payment(payment_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "director", "accountant"))):
    obj = db.get(models.Payment, payment_id)
    if not obj: raise HTTPException(404, "Платёж не найден")
    db.add(Activity(project_code=obj.project_code, actor=user.full_name, action="Удалён платёж", details=f"Платёж #{obj.id}: {obj.amount} {obj.currency}"))
    db.delete(obj); db.commit(); return None

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    obj = db.get(Task, task_id)
    if not obj: raise HTTPException(404, "Задача не найдена")
    if user.role not in {"admin", "director", "project_manager", "office_manager"} and obj.assignee != user.full_name:
        raise HTTPException(403, "Недостаточно прав")
    if obj.project_code: db.add(Activity(project_code=obj.project_code, actor=user.full_name, action="Удалена задача", details=f"{obj.code}: {obj.title}"))
    db.delete(obj); db.commit(); return None


@app.patch("/api/crm/opportunities/{opp_id}/items/{item_id}", response_model=OpportunityItemOut)
def crm_update_opportunity_item(opp_id: int, item_id: int, payload: OpportunityItemIn, db: Session = Depends(get_db), user: User = Depends(require_roles(*CRM_EDIT_ROLES))):
    obj = db.query(models.OpportunityItem).filter_by(id=item_id, opportunity_id=opp_id).first()
    if not obj: raise HTTPException(404, "Позиция потребности не найдена")
    if payload.equipment_id and not db.get(models.Equipment, payload.equipment_id): raise HTTPException(404, "Оборудование не найдено")
    for key, value in payload.model_dump().items(): setattr(obj, key, value)
    crm_audit(db, user, "Изменена позиция потребности", f"{obj.name} × {obj.quantity}")
    db.commit(); db.refresh(obj); return obj
