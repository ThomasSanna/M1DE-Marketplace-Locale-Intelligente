-- =============================================================================
-- Marketplace Locale Intelligente — Tables de Clustering
-- Auteur   : Daniel (Data Engineer)
-- Sprint   : 2 — Pipeline Data & Segmentation
-- Objectif : Stocker les résultats de clustering (clients & producteurs)
--            pour l'API analytique et les dashboards Power BI.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- TABLE : clustering_runs
-- Traçabilité de chaque exécution du pipeline de clustering.
-- Permet la reproductibilité et la comparaison entre exécutions.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS clustering_runs (
    id               SERIAL          PRIMARY KEY,
    run_type         VARCHAR(20)     NOT NULL CHECK (run_type IN ('customer', 'producer')),
    started_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at      TIMESTAMPTZ,
    n_clusters       INTEGER         NOT NULL,
    silhouette_score DECIMAL(5, 4),
    inertia          DECIMAL(14, 2),
    parameters       JSONB,
    status           VARCHAR(20)     NOT NULL DEFAULT 'running'
                     CHECK (status IN ('running', 'success', 'failed'))
);


-- ---------------------------------------------------------------------------
-- TABLE : customer_segments
-- Un enregistrement par client par exécution de clustering.
-- Les features RFM et comportementales sont stockées pour l'explicabilité
-- et l'exploitation directe dans Power BI.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS customer_segments (
    id                      SERIAL          PRIMARY KEY,
    run_id                  INTEGER         NOT NULL REFERENCES clustering_runs(id) ON DELETE CASCADE,
    user_id                 UUID            NOT NULL REFERENCES users(id),
    cluster_id              INTEGER         NOT NULL,
    cluster_label           VARCHAR(100)    NOT NULL,

    -- Features RFM
    recency_days            INTEGER,
    frequency               INTEGER,
    monetary                DECIMAL(10, 2),

    -- Features comportementales
    avg_basket              DECIMAL(10, 2),
    favorite_category       VARCHAR(50),
    cancellation_rate       DECIMAL(5, 4),
    days_since_registration INTEGER,

    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE (run_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_customer_segments_run_id   ON customer_segments(run_id);
CREATE INDEX IF NOT EXISTS idx_customer_segments_user_id  ON customer_segments(user_id);
CREATE INDEX IF NOT EXISTS idx_customer_segments_cluster  ON customer_segments(cluster_id);


-- ---------------------------------------------------------------------------
-- TABLE : producer_segments
-- Un enregistrement par producteur par exécution de clustering.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS producer_segments (
    id                  SERIAL          PRIMARY KEY,
    run_id              INTEGER         NOT NULL REFERENCES clustering_runs(id) ON DELETE CASCADE,
    producer_id         UUID            NOT NULL REFERENCES producers(id),
    cluster_id          INTEGER         NOT NULL,
    cluster_label       VARCHAR(100)    NOT NULL,

    -- Features
    n_products          INTEGER,
    n_categories        INTEGER,
    total_revenue       DECIMAL(12, 2),
    avg_order_value     DECIMAL(10, 2),
    n_orders_received   INTEGER,
    days_active         INTEGER,
    location_region     VARCHAR(100),

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE (run_id, producer_id)
);

CREATE INDEX IF NOT EXISTS idx_producer_segments_run_id       ON producer_segments(run_id);
CREATE INDEX IF NOT EXISTS idx_producer_segments_producer_id  ON producer_segments(producer_id);
CREATE INDEX IF NOT EXISTS idx_producer_segments_cluster      ON producer_segments(cluster_id);


-- ---------------------------------------------------------------------------
-- VUE : v_current_customer_segments
-- Renvoie toujours la dernière exécution réussie.
-- Utilisée par l'API GET /api/v1/data/clustering/customers et Power BI.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_current_customer_segments AS
SELECT
    cs.user_id,
    cs.cluster_id,
    cs.cluster_label,
    cs.recency_days,
    cs.frequency,
    cs.monetary,
    cs.avg_basket,
    cs.favorite_category,
    cs.cancellation_rate,
    cs.days_since_registration,
    u.email,
    u.first_name,
    u.last_name
FROM customer_segments cs
JOIN users u ON u.id = cs.user_id
WHERE cs.run_id = (
    SELECT id FROM clustering_runs
    WHERE run_type = 'customer' AND status = 'success'
    ORDER BY finished_at DESC
    LIMIT 1
);


-- ---------------------------------------------------------------------------
-- VUE : v_current_producer_segments
-- Renvoie toujours la dernière exécution réussie.
-- Utilisée par l'API et Power BI.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_current_producer_segments AS
SELECT
    ps.producer_id,
    ps.cluster_id,
    ps.cluster_label,
    ps.n_products,
    ps.n_categories,
    ps.total_revenue,
    ps.avg_order_value,
    ps.n_orders_received,
    ps.days_active,
    ps.location_region,
    p.farm_name
FROM producer_segments ps
JOIN producers p ON p.id = ps.producer_id
WHERE ps.run_id = (
    SELECT id FROM clustering_runs
    WHERE run_type = 'producer' AND status = 'success'
    ORDER BY finished_at DESC
    LIMIT 1
);
