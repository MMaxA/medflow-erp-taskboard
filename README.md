# MedFlow ERP — Foundation 0.6.3 — CRM CRUD and draft-friendly forms

## Реализовано
- React + TypeScript frontend, подключённый к FastAPI REST API.
- PostgreSQL через Docker Compose (SQLite для локального backend запуска).
- JWT login, `/api/auth/me`, защищённые API endpoints.
- RBAC: director, project_manager, accountant, lawyer, office_manager, admin.
- Серверное хранение проектов и задач.
- Kanban-доска задач в четыре колонки: «К выполнению», «В работе», «На проверке», «Завершено».
- Создание и редактирование задач: название, проект, исполнитель, срок, приоритет и статус.
- Перетаскивание карточек между колонками с сохранением статуса на backend.
- Переназначение исполнителя с уведомлением нового исполнителя.
- Поиск задач по названию, коду, проекту и исполнителю.
- История действий по проектам.
- Базовый endpoint уведомлений и отметки прочтения.
- Демонстрационные пользователи и данные создаются автоматически.

## Запуск (рекомендуется Docker)
1. Установите Docker Desktop и запустите его.
2. В корне проекта:
   `docker compose up --build`
3. API будет доступен на http://localhost:8000, Swagger — http://localhost:8000/docs.
4. В отдельном терминале:
   `cd frontend && npm install && npm run dev`
5. Откройте адрес Vite, обычно http://localhost:5173.

## Демо-учётные записи
Все учётные записи используют пароль `Demo12345!`:
- director@medflow.demo
- manager@medflow.demo
- accountant@medflow.demo
- lawyer@medflow.demo
- office@medflow.demo
- admin@medflow.demo

## Роли и ограничения
- Директор: просмотр пользователей, все данные, управление проектами и задачами.
- Администратор: управление пользователями, все операции MVP.
- Проектный менеджер: создание/изменение проектов и задач.
- Создавать задачу может любой авторизованный пользователь. Редактировать задачу может её исполнитель, офис-менеджер, директор, проектный менеджер или администратор.
- Бухгалтер, юрист, офис-менеджер: авторизованный просмотр; изменение статуса задачи разрешено исполнителю задачи, офис-менеджеру, директору, менеджеру или администратору.
- Проверка ролей выполняется на backend, не только в UI.

## Конфигурация
Backend:
- `DATABASE_URL`
- `SECRET_KEY` — обязательно заменить перед любым развёртыванием вне локальной демонстрации.
- `ACCESS_TOKEN_MINUTES`
- `CORS_ORIGINS`

Frontend:
- По умолчанию API вызывается по относительному адресу `/api` через Vite proxy на `http://localhost:8000` (CORS для локальной разработки не требуется).
- `VITE_API_URL` задавайте только при намеренном подключении к отдельному удалённому API; после изменения `.env` перезапустите Vite.

## Ограничения текущего этапа
- Уведомления: реализован серверный реестр и чтение, но пока нет автоматических триггеров/планировщика генерации и email/push доставки.
- История: логируются создание и редактирование проекта, а также смена статуса связанной задачи; полноценный аудит всех действий будет расширяться.
- Карточка проекта: просмотр и редактирование полей, изменение цены контракта, удаление с подтверждением. При удалении также удаляются связанные задачи и история проекта.
- Пользовательский интерфейс списка пользователей пока демонстрационный; API просмотра и создания пользователей доступно ролям admin/director и admin соответственно.
- Нет refresh-токенов, восстановления пароля, rate limiting, MFA, миграций Alembic и production hardening.
- Демо-пароли и ключ в docker-compose предназначены только для локального прототипа. Измените их перед публикацией.
- Данные вымышленные; не используйте для реальных закупок/договоров.

## Foundation 0.5 — Trading & Finance API (initial backend slice)

This iteration adds persistent PostgreSQL tables for counterparties and payment records. Existing `projects`, `tasks`, users, activity and notifications are retained. SQLAlchemy `create_all()` creates only the new tables on startup; it does not drop or recreate existing data.

### Counterparties
- `GET /api/counterparties` — list; optional `?kind=customer` or `?kind=supplier` (also includes `both`).
- `POST /api/counterparties` — create.
- `PATCH /api/counterparties/{id}` — update.

Counterparty kinds: `customer`, `supplier`, `both`.

### Payments
- `GET /api/payments` — list; optional `?project_code=PR-...` and `?status=planned|paid|cancelled`.
- `POST /api/payments` — create a planned or paid cash-flow record.
- `PATCH /api/payments/{id}` — update a payment.
- `GET /api/projects/{code}/financial-summary` — aggregate paid/planned incoming and outgoing amounts by currency.

Payment directions: `incoming`, `outgoing`. Currencies currently accepted: `EUR`, `BGN`, `USD`, `RUB`. A payment marked `paid` requires `paid_date`. Only admin/director/accountant can create or edit payment records; director, accountant, project manager and admin can read them.

### Storage decision
The document-storage provider is deliberately not coupled to this iteration. The next document milestone should introduce a storage adapter interface and begin with private local storage outside the public frontend directory, with an S3-compatible adapter as a later deployment option.

### Important scope note
This is the first backend slice of the Trading & Finance stage. The UI for counterparties, payment register and document management is not included yet; these API endpoints can be inspected in `/docs`. Financial summary is a management cash-flow view, not statutory accounting or bank reconciliation.

## Foundation 0.6 — CRM and commercial opportunities

This release extends the Foundation 0.5 API with CRM entities and a first working CRM workspace.

### Added backend entities
- `Contact` — contacts linked to a counterparty.
- `Equipment` — corporate equipment catalogue with manufacturer, model, SKU, specifications and registration-document references.
- `Opportunity` — pre-tender commercial opportunity linked to a customer and owner.
- `OpportunityItem` — equipment requirements inside an opportunity.
- `CommercialOffer` — supplier quotation, price, discount, terms and delivery lead times.
- `CostLine` — detailed additional cost lines (logistics, installation, training, security and other costs).

### Added API
- `GET/POST /api/crm/contacts`
- `GET/POST/PATCH /api/crm/equipment`
- `GET/POST/PATCH /api/crm/opportunities`
- `GET/POST/DELETE /api/crm/opportunities/{id}/items`
- `GET/POST /api/crm/offers?opportunity_id={id}`
- `GET/POST /api/crm/opportunities/{id}/costs`
- `GET /api/crm/opportunities/{id}/economics?selling_price=...&currency=...`

CRM write access is available to admin, director, project_manager, office_manager and analyst. Commercial approval is not automated: in line with the agreed setting, the responsible manager owns the decision. Existing accounting and payment records remain separate and are not modified by CRM calculations.

### Economics rules
Equipment cost is calculated from quotation unit price × quantity less the quotation discount. Additional costs are added by currency. Gross profit and margin are calculated only when a selling price in the selected currency is supplied. Amounts in different currencies are intentionally not converted; exchange-rate policy must be agreed before introducing consolidated multi-currency profitability.

### Run
Use the same setup as Foundation 0.5:
- `docker compose up --build` from the project root.
- In `frontend`: `npm install` and `npm run dev`.

The CRM entry is available in the left navigation after login. Add customers and suppliers first, then equipment, opportunities, supplier offers and additional cost lines.

### Limitations of this release
- File/document fields currently store references or text; a secured upload service and versioned document storage are not yet implemented.
- Contacts API supports listing and creation; contact editing/deletion UI is not included yet.
- Opportunity equipment items can be added and removed through the API; the UI currently supports adding from the catalogue.
- No currency conversion, tax accounting, 1C exchange, tender monitoring or FAS case workflow is included.
- `Base.metadata.create_all` creates newly added tables in an existing database; it does not manage schema migrations. Use Alembic before production deployment.
- Full frontend dependency installation/build and Docker integration must be verified in the deployment environment.

## Foundation 0.6.1 — CRM opportunity view and per-offer economics
- Opportunity details now open in a full-screen modal with internal scrolling.
- CRM economics are displayed separately for every supplier offer: equipment net cost after discount, additional costs, total cost, assumed selling price, gross profit and gross margin.
- New additional cost lines can be assigned to a specific offer or marked as general opportunity costs.
- Existing cost lines are preserved as general opportunity costs. An additive startup migration adds the nullable `offer_id` column to existing databases; no database volume reset is required.
- Selling price remains a common comparison assumption for all offers. Currency amounts are not converted; compare offers in the same currency.

## Foundation 0.6.2 — CRM usability improvements
- Restored the explicit “Рассчитать экономику” action in the opportunity dialog.
- Added edit and delete actions for commercial offers. Editing uses `PATCH /api/crm/offers/{offer_id}`; deletion uses `DELETE /api/crm/offers/{offer_id}`.
- Deleting an offer also deletes cost lines explicitly linked to that offer; shared opportunity costs remain untouched.
- Opportunity details now use a large centered modal rather than a full-screen dialog.
- Added color accents to the opportunity pipeline stages and individual offer economics cards.

## Docker: единый образ приложения

Для production-сборки используется один собственный образ `medflow-erp`, который содержит React frontend (сборка Vite, раздача через Nginx) и FastAPI backend (Uvicorn). PostgreSQL остаётся отдельным официальным контейнером с постоянным Docker Volume.

### Локальный запуск

1. Создайте `.env` из шаблона: `Copy-Item .env.example .env` (PowerShell) или `cp .env.example .env`.
2. Задайте уникальные длинные значения `POSTGRES_PASSWORD` и `SECRET_KEY`. Для `POSTGRES_PASSWORD` в текущем формате `DATABASE_URL` используйте латинские буквы и цифры.
3. Проверьте конфигурацию: `docker compose config`.
4. Соберите и запустите: `docker compose up -d --build`.
5. Откройте `http://localhost:8080`; API health: `http://localhost:8080/api/health`; Swagger: `http://localhost:8080/docs`.

### Публикация единого образа в Docker Hub

Укажите свой Docker Hub namespace в `.env` через `DOCKERHUB_USERNAME`, затем выполните:

```bash
docker login
docker compose build app
docker compose push app
```

Образ публикуется как `${DOCKERHUB_USERNAME}/medflow-erp:${IMAGE_TAG}`. Сервис PostgreSQL не публикуется в вашем namespace: используется официальный `postgres:16-alpine`.

### Запуск на VPS

Перенесите на VPS `docker-compose.yml` и `.env` (не публикуйте `.env` в Git), затем выполните:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Перед первым production-запуском замените секреты. В проекте предусмотрены демонстрационные учётные записи с общим паролем `Demo12345!`; смените их пароли сразу после первого входа и не используйте демонстрационные реквизиты в открытом доступе.

### Обновление версии

Измените `IMAGE_TAG` в `.env`, соберите новый образ и опубликуйте его. На VPS обновите `IMAGE_TAG`, затем выполните `docker compose pull && docker compose up -d`.
