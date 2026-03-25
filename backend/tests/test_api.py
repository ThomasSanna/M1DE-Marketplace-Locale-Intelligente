import uuid
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient

import models
from api.v1.dependencies import get_current_user
from database import get_db
from main import app


client = TestClient(app)


class FakeQuery:
    def __init__(self, first_value=None, all_value=None):
        self._first_value = first_value
        self._all_value = all_value

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def offset(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def first(self):
        return self._first_value

    def all(self):
        if self._all_value is not None:
            return self._all_value
        if self._first_value is None:
            return []
        if isinstance(self._first_value, list):
            return self._first_value
        return [self._first_value]


class FakeSession:
    def __init__(self, orders=None, products=None, producer=None):
        self.orders = orders or []
        self.products = products or []
        self.producer = producer

    def query(self, model):
        if model is models.Order:
            first_order = self.orders[0] if self.orders else None
            return FakeQuery(first_value=first_order, all_value=self.orders)
        if model is models.Product:
            first_product = self.products[0] if self.products else None
            return FakeQuery(first_value=first_product, all_value=self.products)
        if model is models.Producer:
            return FakeQuery(first_value=self.producer, all_value=[self.producer] if self.producer else [])
        raise AssertionError(f"Unsupported query model: {model}")

    def add(self, obj):
        if isinstance(obj, models.Order) and obj not in self.orders:
            if obj.id is None:
                obj.id = uuid.uuid4()
            if obj.created_at is None:
                obj.created_at = datetime.utcnow()
            if obj.updated_at is None:
                obj.updated_at = datetime.utcnow()
            self.orders.append(obj)
        if isinstance(obj, models.OrderItem) and obj.id is None:
            obj.id = uuid.uuid4()

    def flush(self):
        for order in self.orders:
            if order.id is None:
                order.id = uuid.uuid4()
            if order.created_at is None:
                order.created_at = datetime.utcnow()
            if order.updated_at is None:
                order.updated_at = datetime.utcnow()

    def commit(self):
        return None

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


def test_create_order_returns_draft_with_items():
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=uuid.uuid4(),
        name="Pommes",
        category=models.ProductCategory.fruits,
        price=Decimal("4.90"),
        stock_quantity=Decimal("30.000"),
        unit=models.ProductUnit.kg,
        is_active=True,
    )
    fake_db = FakeSession(products=[product])
    client_user = models.User(
        id=uuid.uuid4(),
        email="client@test.local",
        password_hash="x",
        role=models.UserRole.client,
        first_name="Client",
        last_name="Test",
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    app.dependency_overrides[get_current_user] = _override_user(client_user)

    response = client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": str(product.id), "quantity": 2}]},
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "draft"
    assert payload["total_amount"] == 9.8
    assert len(payload["items"]) == 1


def test_list_orders_returns_client_history():
    client_id = uuid.uuid4()
    order = models.Order(
        id=uuid.uuid4(),
        client_id=client_id,
        status=models.OrderStatus.draft,
        total_amount=Decimal("12.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    order.items = []

    fake_db = FakeSession(orders=[order])
    client_user = models.User(
        id=client_id,
        email="client@test.local",
        password_hash="x",
        role=models.UserRole.client,
        first_name="Client",
        last_name="Test",
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    app.dependency_overrides[get_current_user] = _override_user(client_user)

    response = client.get("/api/v1/orders")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["id"] == str(order.id)


def test_order_status_lifecycle_transitions_are_controlled():
    producer_user_id = uuid.uuid4()
    producer = models.Producer(
        id=uuid.uuid4(),
        user_id=producer_user_id,
        farm_name="Ferme Test",
        location_city="Nantes",
        location_region="Pays de la Loire",
    )
    product = models.Product(
        id=uuid.uuid4(),
        producer_id=producer.id,
        name="Carottes",
        category=models.ProductCategory.legumes,
        price=Decimal("3.00"),
        stock_quantity=Decimal("20.000"),
        unit=models.ProductUnit.kg,
        is_active=True,
    )
    order = models.Order(
        id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        status=models.OrderStatus.confirmed,
        total_amount=Decimal("15.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    order.items = [
        models.OrderItem(
            id=uuid.uuid4(),
            order_id=order.id,
            product_id=product.id,
            quantity=Decimal("5.000"),
            unit_price_snapshot=Decimal("3.00"),
        )
    ]

    fake_db = FakeSession(orders=[order], products=[product], producer=producer)
    producer_user = models.User(
        id=producer_user_id,
        email="producer@test.local",
        password_hash="x",
        role=models.UserRole.producer,
        first_name="Producer",
        last_name="Test",
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    app.dependency_overrides[get_current_user] = _override_user(producer_user)

    shipped_response = client.patch(
        f"/api/v1/orders/{order.id}/status",
        json={"status": "shipped"},
    )
    delivered_response = client.patch(
        f"/api/v1/orders/{order.id}/status",
        json={"status": "delivered"},
    )
    invalid_response = client.patch(
        f"/api/v1/orders/{order.id}/status",
        json={"status": "cancelled"},
    )

    app.dependency_overrides.clear()

    assert shipped_response.status_code == 200
    assert delivered_response.status_code == 200
    assert invalid_response.status_code == 403
