from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.schemas import ProjectIn, PaymentIn, OfferIn, CostLineIn, TaskStatusIn

def test_money_inputs_are_decimal_and_have_cent_precision():
    project = ProjectIn(code="PR-1", name="Example", customer="Customer", amount="123456789.12")
    payment = PaymentIn(project_code="PR-1", direction="incoming", amount="0.10")
    assert project.amount == Decimal("123456789.12")
    assert payment.amount == Decimal("0.10")

@pytest.mark.parametrize("amount", ["-0.01", "1000000000000", "1.001"])
def test_payment_rejects_invalid_money(amount):
    with pytest.raises(ValidationError):
        PaymentIn(project_code="PR-1", direction="incoming", amount=amount)

def test_task_status_rejects_unknown_values():
    with pytest.raises(ValidationError):
        TaskStatusIn(status="anything")

def test_cost_and_offer_amounts_use_decimal():
    cost = CostLineIn(category="Delivery", amount="0.30")
    offer = OfferIn(opportunity_id=1, supplier_id=1, unit_price="10.25")
    assert cost.amount == Decimal("0.30")
    assert offer.unit_price == Decimal("10.25")
