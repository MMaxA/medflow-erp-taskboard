from app.database import SessionLocal
from app.models import User, Task
from app.security import hash_password, create_access_token

def test_task_owner_can_change_status_but_other_user_cannot(client):
    with SessionLocal() as db:
        db.query(Task).delete()
        db.query(User).delete()
        owner = User(email="owner@example.test", full_name="Task Owner", role="accountant", password_hash=hash_password("long-test-password"))
        other = User(email="other@example.test", full_name="Other User", role="lawyer", password_hash=hash_password("long-test-password"))
        db.add_all([owner, other])
        db.flush()
        task = Task(code="TS-TEST", title="Access test", assignee=owner.full_name, assignee_id=owner.id, status="Новая")
        db.add(task)
        db.commit()
        task_id, owner_email, other_email = task.id, owner.email, other.email

    denied = client.patch(f"/api/tasks/{task_id}/status", json={"status": "В работе"}, headers={"Authorization": f"Bearer {create_access_token(other_email)}"})
    assert denied.status_code == 403

    allowed = client.patch(f"/api/tasks/{task_id}/status", json={"status": "В работе"}, headers={"Authorization": f"Bearer {create_access_token(owner_email)}"})
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "В работе"

    invalid = client.patch(f"/api/tasks/{task_id}/status", json={"status": "made-up"}, headers={"Authorization": f"Bearer {create_access_token(owner_email)}"})
    assert invalid.status_code == 422
