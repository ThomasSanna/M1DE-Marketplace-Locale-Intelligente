import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, cast

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


class FakeExecuteResult:
    def __init__(self, payload):
        self._payload = payload

    def mappings(self):
        return self

    def first(self):
        if self._payload is None:
            return None
        if isinstance(self._payload, list):
            return self._payload[0] if self._payload else None
        return self._payload

    def all(self):
        if self._payload is None:
            return []
        if isinstance(self._payload, list):
            return self._payload
        return [self._payload]


class FakeSession:
    def __init__(self, orders=None, products=None, producer=None, execute_results=None):
        self.orders = orders or []
        self.products = products or []
        self.producer = producer
        self.execute_results = execute_results or {}

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
            order_obj = cast(Any, obj)
            if order_obj.id is None:
                order_obj.id = uuid.uuid4()
            if order_obj.created_at is None:
                order_obj.created_at = datetime.utcnow()
            if order_obj.updated_at is None:
                order_obj.updated_at = datetime.utcnow()
            self.orders.append(obj)
        if isinstance(obj, models.OrderItem) and obj.id is None:
            item_obj = cast(Any, obj)
            item_obj.id = uuid.uuid4()

    def flush(self):
        for order in self.orders:
            order_obj = cast(Any, order)
            if order_obj.id is None:
                order_obj.id = uuid.uuid4()
            if order_obj.created_at is None:
                order_obj.created_at = datetime.utcnow()
            if order_obj.updated_at is None:
                order_obj.updated_at = datetime.utcnow()

    def commit(self):
        return None

    def refresh(self, obj):
        return None

    def execute(self, statement, params=None):
        statement_text = str(statement)
        for marker, payload in self.execute_results.items():
            if marker in statement_text:
                if callable(payload):
                    resolved_payload = payload(params or {})
                else:
                    resolved_payload = payload
                return FakeExecuteResult(resolved_payload)
        raise AssertionError(f"Unsupported SQL statement: {statement_text}")


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


def test_metrics_endpoint_exposes_prometheus_metrics():
    client.get("/")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "http_request_duration_seconds" in body
    assert "http_requests_total" in body
    assert "http_requests_success_total" in body
    assert "http_requests_error_total" in body


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


def test_data_sales_metrics_endpoint_returns_aggregates():
    fake_db = FakeSession(
        execute_results={
            "FROM v_sales_summary v": {
                "total_revenue": 1542.7,
                "average_basket": 31.48,
                "total_orders": 49,
            }
        }
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    response = client.get("/api/v1/data/sales-metrics")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_revenue"] == 1542.7
    assert payload["average_basket"] == 31.48
    assert payload["total_orders"] == 49


def test_data_customers_clustering_endpoint_returns_latest_segments():
    run_id = 12
    user_id = uuid.uuid4()

    fake_db = FakeSession(
        execute_results={
            "FROM clustering_runs": {"run_id": run_id, "n_clusters": 4},
            "FROM customer_segments\nWHERE run_id = :run_id": lambda params: {
                "segments_count": 1,
            },
            "FROM customer_segments cs": [
                {
                    "user_id": user_id,
                    "cluster_id": 2,
                    "cluster_label": "Fideles premium",
                    "recency_days": 7,
                    "frequency": 8,
                    "monetary": 240.5,
                    "avg_basket": 30.06,
                    "favorite_category": "fruits",
                    "cancellation_rate": 0.0,
                    "days_since_registration": 120,
                    "email": "client.segment@example.com",
                    "first_name": "Alice",
                    "last_name": "Martin",
                }
            ],
        }
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    response = client.get("/api/v1/data/clustering/customers")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == run_id
    assert payload["n_clusters"] == 4
    assert payload["segments_count"] == 1
    assert len(payload["segments"]) == 1
    assert payload["segments"][0]["cluster_label"] == "Fideles premium"


def test_data_anomalies_endpoint_returns_failed_payments():
    payment_id = uuid.uuid4()
    order_id = uuid.uuid4()
    client_id = uuid.uuid4()

    fake_db = FakeSession(
        execute_results={
            "FROM payments p\nWHERE p.status = 'failed' OR p.is_simulated_error = TRUE": {
                "total_anomalies": 1,
            },
            "FROM payments p\nJOIN orders o ON o.id = p.order_id": [
                {
                    "payment_id": payment_id,
                    "order_id": order_id,
                    "client_id": client_id,
                    "client_email": "fraud.alert@example.com",
                    "amount": 89.9,
                    "payment_status": "failed",
                    "order_status": "draft",
                    "is_simulated_error": True,
                    "detected_at": datetime.utcnow(),
                    "anomaly_type": "simulated_payment_error",
                }
            ],
        }
    )

    app.dependency_overrides[get_db] = _override_db(fake_db)
    response = client.get("/api/v1/data/anomalies")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_anomalies"] == 1
    assert len(payload["anomalies"]) == 1
    assert payload["anomalies"][0]["payment_status"] == "failed"
    assert payload["anomalies"][0]["anomaly_type"] == "simulated_payment_error"