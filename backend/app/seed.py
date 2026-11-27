from sqlalchemy.orm import Session
from .models import User,Project,Task,Notification,Activity
from .security import hash_password
from .config import settings
DEMO_USERS=[
("director@medflow.demo","Демо-директор","director"),
("manager@medflow.demo","Анна Смирнова","project_manager"),
("accountant@medflow.demo","Елена Кузнецова","accountant"),
("lawyer@medflow.demo","Демо-юрист","lawyer"),
("office@medflow.demo","Демо-офис-менеджер","office_manager"),
("admin@medflow.demo","Администратор","admin")]
def seed(db:Session):
    if settings.bootstrap_admin_email and settings.bootstrap_admin_password:
        if not db.query(User).filter_by(email=settings.bootstrap_admin_email).first():
            db.add(User(email=settings.bootstrap_admin_email, full_name="System Administrator", role="admin", password_hash=hash_password(settings.bootstrap_admin_password)))
    if settings.demo_seed:
        for email,name,role in DEMO_USERS:
            if not db.query(User).filter_by(email=email).first():
                db.add(User(email=email,full_name=name,role=role,password_hash=hash_password("Demo12345!")))
    db.flush()
    if settings.demo_seed and db.query(Project).count()==0:
        rows=[
        ("PR-001","Поставка УЗИ-комплекса","ГКБ № 4 (демо)","УЗИ экспертного класса","Подготовка процедуры","Анна Смирнова",5800000,75,"Подбор комплектации и согласование технических характеристик."),
        ("PR-002","Оснащение кабинета эндоскопии","Областной диагностический центр (демо)","Эндоскопическая система","КП и подбор","Анна Смирнова",4200000,45,"Проработка потребности, сбор предложений и оценка финансирования."),
        ("PR-003","Поставка рентгеновской системы","Центральная районная больница (демо)","Рентгеновский комплекс","Закупка","Анна Смирнова",9600000,80,"Опубликована закупка, готовится заявка."),
        ("PR-004","Модернизация лаборатории","Клиническая лаборатория (демо)","Лабораторный анализатор","Исполнение","Сергей Волков",3100000,100,"Контракт заключён, контроль поставки и приёмки.")]
        for r in rows: db.add(Project(code=r[0],name=r[1],customer=r[2],product=r[3],stage=r[4],owner=r[5],amount=r[6],probability=r[7],description=r[8]))
    if settings.demo_seed and db.query(Task).count()==0:
        rows=[("TS-101","Проверить технические характеристики УЗИ-комплекса","PR-001","Анна Смирнова","2026-11-21","В работе","Высокий"),("TS-102","Запросить обновлённое КП производителя","PR-001","Иван Петров","2026-11-22","Новая","Средний"),("TS-103","Подготовить черновик заявки","PR-003","Анна Смирнова","2026-11-23","На проверке","Высокий"),("TS-104","Подтвердить готовность помещения","PR-004","Сергей Волков","2026-11-24","В работе","Средний")]
        for r in rows: db.add(Task(code=r[0],title=r[1],project_code=r[2],assignee=r[3],due_date=r[4],status=r[5],priority=r[6]))
    db.commit()
