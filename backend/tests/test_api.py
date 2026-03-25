import uuid
from decimal import Decimal

from fastapi.testclient import TestClient

from main import app
from api.v1.dependencies import get_current_user
from database import get_db
import models


client = TestClient(app)


class FakeQuery:
    def __init__(self, value_getter):
        self._value_getter = value_getter

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._value_getter()

    def offset(self, _skip):
        return self

    def limit(self, _limit):
        return self

    def all(self):
        value = self._value_getter()
        if isinstance(value, list):
            return value
        return []


class FakeSession:
    def __init__(self, order=None, payment=None, products=None):
        self.order = order
        self.payment = payment
        self.products = products or []
        self.commit_count = 0

    def query(self, model):
        if model is models.Order:
            return FakeQuery(lambda: self.order)
        if model is models.Payment:
            return FakeQuery(lambda: self.payment)
        if model is models.Product:
            return FakeQuery(lambda: self.products)
        raise AssertionError(f"Unsupported model query: {model}")

    def add(self, obj):
        if isinstance(obj, models.Payment):
            self.payment = obj

    def commit(self):
        self.commit_count += 1

    def refresh(self, obj):
        return None


def _override_db(fake_session):
    def _override():
        yield fake_session

    return _override


def _override_user(user):
    def _override():
        return user

    return _override


def test_root_returns_welcome_message():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_products_list_endpoint_exists():
    app.dependency_overrides[get_db] = _override_db(FakeSession(products=[]))
    response = client.get("/api/v1/products/")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


def test_payments_success_scenario_confirms_order():
    user_id = uuid.uuid4()
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=uuid.uuid4(),
        name="Pommes",
        category=models.ProductCategory.fruits,
        price=Decimal("4.90"),
        stock_quantity=Decimal("10.000"),
        unit=models.ProductUnit.kg,
        is_active=True,
    )
    order_item = models.OrderItem(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_id=product.id,
        quantity=Decimal("2.000"),
        unit_price_snapshot=Decimal("4.90"),
    )
    order_item.product = product
    order = models.Order(
        id=uuid.uuid4(),
        client_id=user_id,
        status=models.OrderStatus.draft,
        total_amount=Decimal("49.90"),
    )
    order.items = [order_item]
    fake_session = FakeSession(order=order)

    app.dependency_overrides[get_db] = _override_db(fake_session)
    app.dependency_overrides[get_current_user] = _override_user(
        models.User(id=user_id, role=models.UserRole.client, email="client@test.local", password_hash="x", first_name="T", last_name="U")
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "order_id": str(order.id),
            "simulate_scenario": "success",
            "processing_delay_ms": 0,
            "idempotency_key": "idem-success-001",
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["order_status"] == "confirmed"
    assert payload["amount"] == 49.9
    assert Decimal(str(product.stock_quantity)) == Decimal("8.000")


def test_payments_controlled_error_returns_expected_code():
    user_id = uuid.uuid4()
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=uuid.uuid4(),
        name="Lait",
        category=models.ProductCategory.produits_laitiers,
        price=Decimal("2.50"),
        stock_quantity=Decimal("6.000"),
        unit=models.ProductUnit.piece,
        is_active=True,
    )
    order_item = models.OrderItem(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_id=product.id,
        quantity=Decimal("1.000"),
        unit_price_snapshot=Decimal("2.50"),
    )
    order_item.product = product
    order = models.Order(
        id=uuid.uuid4(),
        client_id=user_id,
        status=models.OrderStatus.draft,
        total_amount=Decimal("19.00"),
    )
    order.items = [order_item]
    fake_session = FakeSession(order=order)

    app.dependency_overrides[get_db] = _override_db(fake_session)
    app.dependency_overrides[get_current_user] = _override_user(
        models.User(id=user_id, role=models.UserRole.client, email="client@test.local", password_hash="x", first_name="T", last_name="U")
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "order_id": str(order.id),
            "simulate_scenario": "insufficient_funds",
            "processing_delay_ms": 0,
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 402
    detail = response.json()["detail"]
    assert detail["error_code"] == "INSUFFICIENT_FUNDS"
    assert detail["retryable"] is False


def test_payments_idempotency_replays_same_result_without_second_commit():
    user_id = uuid.uuid4()
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=uuid.uuid4(),
        name="Carottes",
        category=models.ProductCategory.legumes,
        price=Decimal("3.00"),
        stock_quantity=Decimal("9.000"),
        unit=models.ProductUnit.kg,
        is_active=True,
    )
    order_item = models.OrderItem(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_id=product.id,
        quantity=Decimal("2.000"),
        unit_price_snapshot=Decimal("3.00"),
    )
    order_item.product = product
    order = models.Order(
        id=uuid.uuid4(),
        client_id=user_id,
        status=models.OrderStatus.draft,
        total_amount=Decimal("12.50"),
    )
    order.items = [order_item]
    fake_session = FakeSession(order=order)

    app.dependency_overrides[get_db] = _override_db(fake_session)
    app.dependency_overrides[get_current_user] = _override_user(
        models.User(id=user_id, role=models.UserRole.client, email="client@test.local", password_hash="x", first_name="T", last_name="U")
    )

    payload = {
        "order_id": str(order.id),
        "simulate_scenario": "success",
        "processing_delay_ms": 0,
        "idempotency_key": "idem-repeat-001",
    }
    first_response = client.post("/api/v1/payments", json=payload)
    second_response = client.post("/api/v1/payments", json=payload)
    app.dependency_overrides.clear()

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first_payload = first_response.json()
    second_payload = second_response.json()
    assert second_payload["provider_reference"] == first_payload["provider_reference"]
    assert fake_session.commit_count == 1
    assert Decimal(str(product.stock_quantity)) == Decimal("7.000")


def test_payments_returns_409_when_stock_is_insufficient():
    user_id = uuid.uuid4()
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=uuid.uuid4(),
        name="Tomates",
        category=models.ProductCategory.legumes,
        price=Decimal("5.00"),
        stock_quantity=Decimal("1.000"),
        unit=models.ProductUnit.kg,
        is_active=True,
    )
    order_item = models.OrderItem(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_id=product.id,
        quantity=Decimal("3.000"),
        unit_price_snapshot=Decimal("5.00"),
    )
    order_item.product = product
    order = models.Order(
        id=uuid.uuid4(),
        client_id=user_id,
        status=models.OrderStatus.draft,
        total_amount=Decimal("15.00"),
    )
    order.items = [order_item]
    fake_session = FakeSession(order=order)

    app.dependency_overrides[get_db] = _override_db(fake_session)
    app.dependency_overrides[get_current_user] = _override_user(
        models.User(id=user_id, role=models.UserRole.client, email="client@test.local", password_hash="x", first_name="T", last_name="U")
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "order_id": str(order.id),
            "simulate_scenario": "success",
            "processing_delay_ms": 0,
        },
    )
    app.dependency_overrides.clear()

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail.get("error_code") == "INSUFFICIENT_STOCK"
    assert Decimal(str(product.stock_quantity)) == Decimal("1.000")
