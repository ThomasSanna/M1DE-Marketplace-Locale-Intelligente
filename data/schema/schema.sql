-- =============================================================================
-- Marketplace Locale Intelligente — Schéma PostgreSQL
-- Auteur   : Daniel (Data Engineer)
-- Sprint   : 1 — Fondations
-- Objectif : Couvrir les US1.1, US1.2, US1.3 tout en anticipant les besoins
--            analytiques (clustering, anomalies, prédiction des ventes).
-- =============================================================================


-- ---------------------------------------------------------------------------
-- TYPES ÉNUMÉRÉS
-- ---------------------------------------------------------------------------

CREATE TYPE user_role     AS ENUM ('client', 'producer');
CREATE TYPE order_status  AS ENUM ('draft', 'confirmed', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'success', 'failed');
CREATE TYPE product_unit  AS ENUM ('kg', 'g', 'litre', 'piece', 'bouquet', 'boite');
CREATE TYPE product_category AS ENUM (
    'fruits', 'legumes', 'viandes', 'poissons',
    'produits_laitiers', 'epicerie', 'boissons', 'autres'
);


-- ---------------------------------------------------------------------------
-- TABLE : users
-- Couvre : US1.1 (inscription), US1.2 (login + profil)
-- Analytique :
--   • role          → segmentation client vs producteur
--   • created_at    → cohortes d'inscription, churn analysis
--   • last_login_at → mesure d'activité / inactivité (comportement)
-- ---------------------------------------------------------------------------

CREATE TABLE users (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   VARCHAR(255)    NOT NULL,
    role            user_role       NOT NULL,
    first_name      VARCHAR(100)    NOT NULL,
    last_name       VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20),

    -- [DATA] Suivi temporel indispensable pour les analyses de cohortes
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    -- [DATA] Fréquence de connexion → feature pour clustering comportemental
    last_login_at   TIMESTAMPTZ
);

CREATE INDEX idx_users_role       ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);


-- ---------------------------------------------------------------------------
-- TABLE : producers
-- Profil étendu des utilisateurs de rôle 'producer'.
-- Couvre : US1.1 (inscription producteur), US1.3 (liste producteurs)
-- Analytique :
--   • location_region → analyse géographique des ventes
--   • created_at      → ancienneté du producteur (feature ML)
-- ---------------------------------------------------------------------------

CREATE TABLE producers (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID            NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    farm_name       VARCHAR(200)    NOT NULL,

    -- [DATA] Granularité géographique nécessaire pour le clustering géo
    location_city   VARCHAR(100)    NOT NULL,
    location_region VARCHAR(100)    NOT NULL,
    location_lat    DECIMAL(9, 6),
    location_lng    DECIMAL(9, 6),

    description     TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_producers_region ON producers(location_region);


-- ---------------------------------------------------------------------------
-- TABLE : products
-- Couvre : US1.3 (catalogue + détail produit)
-- Analytique :
--   • category      → segmentation des achats par type de produit
--   • price         → analyse tarifaire, panier moyen
--   • stock_quantity → détection de ruptures (anomalie)
--   • created_at    → cycle de vie produit
-- ---------------------------------------------------------------------------

CREATE TABLE products (
    id              UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    producer_id     UUID                NOT NULL REFERENCES producers(id) ON DELETE CASCADE,
    name            VARCHAR(200)        NOT NULL,
    description     TEXT,
    category        product_category    NOT NULL,
    price           DECIMAL(10, 2)      NOT NULL CHECK (price >= 0),
    stock_quantity  DECIMAL(10, 3)      NOT NULL CHECK (stock_quantity >= 0),
    unit            product_unit        NOT NULL DEFAULT 'piece',
    is_active       BOOLEAN             NOT NULL DEFAULT TRUE,

    -- [DATA] Horodatage pour l'analyse du cycle de vie des produits
    created_at      TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_producer_id ON products(producer_id);
CREATE INDEX idx_products_category    ON products(category);
CREATE INDEX idx_products_is_active   ON products(is_active);


-- ---------------------------------------------------------------------------
-- TABLE : orders
-- Couvre : Sprint 2 (cycle de vie commande) — anticipé pour le mock data
-- Analytique :
--   • status        → taux de conversion, abandons de panier
--   • total_amount  → distribution du panier moyen
--   • created_at    → saisonnalité des achats, séries temporelles
-- ---------------------------------------------------------------------------

CREATE TABLE orders (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       UUID            NOT NULL REFERENCES users(id),
    status          order_status    NOT NULL DEFAULT 'draft',

    -- [DATA] Snapshot du montant final (ne pas recalculer depuis order_items)
    total_amount    DECIMAL(10, 2)  NOT NULL DEFAULT 0.00,

    -- [DATA] Timestamps horodatés → features temporelles pour la prédiction
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    confirmed_at    TIMESTAMPTZ,
    delivered_at    TIMESTAMPTZ
);

CREATE INDEX idx_orders_client_id  ON orders(client_id);
CREATE INDEX idx_orders_status     ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);


-- ---------------------------------------------------------------------------
-- TABLE : order_items
-- Détail ligne par ligne de chaque commande.
-- Analytique :
--   • unit_price_snapshot → prix au moment de l'achat (drift tarifaire)
--   • quantity            → volumes achetés par produit (top produits)
-- ---------------------------------------------------------------------------

CREATE TABLE order_items (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID            NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id          UUID            NOT NULL REFERENCES products(id),

    quantity            DECIMAL(10, 3)  NOT NULL CHECK (quantity > 0),

    -- [DATA] Snapshot du prix : indispensable — le prix produit peut changer
    unit_price_snapshot DECIMAL(10, 2)  NOT NULL CHECK (unit_price_snapshot >= 0)
);

CREATE INDEX idx_order_items_order_id   ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);


-- ---------------------------------------------------------------------------
-- TABLE : payments
-- Couvre : POST /api/v1/payments (simulateur avec 5% d'erreur volontaire)
-- Analytique :
--   • status = 'failed' → source principale pour la détection d'anomalies
--   • is_simulated_error → flag permettant de distinguer erreur voulue vs bug réel
--   • created_at        → densité temporelle des paiements échoués
-- ---------------------------------------------------------------------------

CREATE TABLE payments (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID            NOT NULL UNIQUE REFERENCES orders(id),
    amount              DECIMAL(10, 2)  NOT NULL,
    status              payment_status  NOT NULL DEFAULT 'pending',

    -- [DATA] Flag critique : distingue l'erreur simulée (5%) du vrai incident
    is_simulated_error  BOOLEAN         NOT NULL DEFAULT FALSE,

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payments_status     ON payments(status);
CREATE INDEX idx_payments_created_at ON payments(created_at);


-- ---------------------------------------------------------------------------
-- VUE ANALYTIQUE : v_sales_summary
-- Pré-agrégation pour les endpoints /api/v1/data/sales-metrics
-- et pour les connexions PowerBI (Manon).
-- ---------------------------------------------------------------------------

CREATE VIEW v_sales_summary AS
SELECT
    p.category,
    pr.location_region,
    DATE_TRUNC('day', o.created_at)     AS sale_day,
    COUNT(DISTINCT o.id)                AS nb_orders,
    SUM(oi.quantity * oi.unit_price_snapshot) AS revenue,
    AVG(o.total_amount)                 AS avg_basket
FROM order_items oi
JOIN orders   o  ON o.id  = oi.order_id
JOIN products p  ON p.id  = oi.product_id
JOIN producers pr ON pr.id = p.producer_id
WHERE o.status IN ('confirmed', 'delivered')
GROUP BY p.category, pr.location_region, DATE_TRUNC('day', o.created_at);
