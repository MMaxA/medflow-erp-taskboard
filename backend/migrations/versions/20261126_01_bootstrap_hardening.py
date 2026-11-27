"""Adopt legacy schema into Alembic and bind tasks to users."""
from alembic import op
from sqlalchemy import inspect, text
from app.database import Base
from app import models

revision = "20261126_01"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    # create_all initializes an empty installation; on the existing MVP it is additive.
    Base.metadata.create_all(bind=bind)
    columns = {c["name"] for c in inspect(bind).get_columns("tasks")}
    if "assignee_id" not in columns:
        op.add_column("tasks", models.Task.__table__.c.assignee_id.copy())
    if "ix_tasks_assignee_id" not in {i["name"] for i in inspect(bind).get_indexes("tasks")}:
        op.create_index("ix_tasks_assignee_id", "tasks", ["assignee_id"])
    project_columns = {c["name"] for c in inspect(bind).get_columns("projects")}
    if "owner_id" not in project_columns:
        op.add_column("projects", models.Project.__table__.c.owner_id.copy())
    if "ix_projects_owner_id" not in {i["name"] for i in inspect(bind).get_indexes("projects")}:
        op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    cost_columns = {c["name"] for c in inspect(bind).get_columns("cost_lines")}
    if "offer_id" not in cost_columns:
        op.add_column("cost_lines", models.CostLine.__table__.c.offer_id.copy())
    if "ix_cost_lines_offer_id" not in {i["name"] for i in inspect(bind).get_indexes("cost_lines")}:
        op.create_index("ix_cost_lines_offer_id", "cost_lines", ["offer_id"])
    bind.execute(text("UPDATE tasks SET assignee_id = (SELECT MIN(id) FROM users WHERE users.full_name = tasks.assignee GROUP BY full_name HAVING COUNT(*) = 1) WHERE assignee_id IS NULL AND assignee <> '' AND (SELECT COUNT(*) FROM users WHERE users.full_name = tasks.assignee) = 1"))
    bind.execute(text("UPDATE projects SET owner_id = (SELECT MIN(id) FROM users WHERE users.full_name = projects.owner GROUP BY full_name HAVING COUNT(*) = 1) WHERE owner_id IS NULL AND owner <> '' AND (SELECT COUNT(*) FROM users WHERE users.full_name = projects.owner) = 1"))
    if bind.dialect.name == "postgresql":
        too_large=bind.execute(text("SELECT COUNT(*) FROM projects WHERE amount > 999999999999.99 OR amount < 0")).scalar_one()
        if too_large:
            raise RuntimeError("Projects contain amounts outside Numeric(14,2); reconcile those values before migrating")
        op.alter_column("projects", "amount", type_=models.Project.__table__.c.amount.type, postgresql_using="amount::numeric(14,2)")

def downgrade():
    op.drop_index("ix_tasks_assignee_id", table_name="tasks")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_index("ix_cost_lines_offer_id", table_name="cost_lines")
    op.drop_column("tasks", "assignee_id")
    op.drop_column("projects", "owner_id")
    op.drop_column("cost_lines", "offer_id")
