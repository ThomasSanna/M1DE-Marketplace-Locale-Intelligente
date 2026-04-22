-- =============================================================================
-- Marketplace Locale Intelligente — Tables de Détection d'Anomalies
-- Auteur   : Daniel (Data Engineer)
-- Sprint   : 3 — Pipeline Data final (détection anomalies)
-- Objectif : Stocker les résultats de détection d'anomalies (paiements,
--            commandes) pour l'API analytique et les dashboards Power BI.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- TABLE : anomaly_runs
-- Traçabilité de chaque exécution du pipeline de détection d'anomalies.
-- Même logique que clustering_runs pour la reproductibilité.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS anomaly_runs (
    id               SERIAL          PRIMARY KEY,
    started_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    finished_at      TIMESTAMPTZ,
    algorithm        VARCHAR(50)     NOT NULL DEFAULT 'IsolationForest',
    n_anomalies      INTEGER,
    contamination    DECIMAL(5, 4),
    parameters       JSONB,
    status           VARCHAR(20)     NOT NULL DEFAULT 'running'
                     CHECK (status IN ('running', 'success', 'failed'))
);


-- ---------------------------------------------------------------------------
-- TABLE : anomalies
-- Un enregistrement par transaction détectée comme anormale.
-- Stocke les features utilisées pour l'explicabilité.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS anomalies (
    id                  SERIAL          PRIMARY KEY,
    run_id              INTEGER         NOT NULL REFERENCES anomaly_runs(id) ON DELETE CASCADE,
    order_id            UUID            NOT NULL REFERENCES orders(id),
    client_id           UUID            NOT NULL REFERENCES users(id),
    anomaly_score       DECIMAL(8, 4)   NOT NULL,
    anomaly_type        VARCHAR(100),

    -- Features utilisées pour la détection
    order_amount        DECIMAL(10, 2),
    payment_failed      BOOLEAN,
    is_simulated_error  BOOLEAN,
    n_items             INTEGER,
    avg_item_price      DECIMAL(10, 2),
    hour_of_day         INTEGER,
    day_of_week         INTEGER,
    days_since_last_order INTEGER,
    client_avg_basket   DECIMAL(10, 2),
    amount_vs_avg_ratio DECIMAL(8, 4),

    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    UNIQUE (run_id, order_id)
);

CREATE INDEX IF NOT EXISTS idx_anomalies_run_id    ON anomalies(run_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_order_id  ON anomalies(order_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_client_id ON anomalies(client_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_score     ON anomalies(anomaly_score);


-- ---------------------------------------------------------------------------
-- VUE : v_current_anomalies
-- Renvoie les anomalies de la dernière exécution réussie.
-- Utilisée par l'API GET /api/v1/data/anomalies et Power BI.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW v_current_anomalies AS
SELECT
    a.order_id,
    a.client_id,
    u.email           AS client_email,
    u.first_name      AS client_first_name,
    u.last_name       AS client_last_name,
    a.anomaly_score,
    a.anomaly_type,
    a.order_amount,
    a.payment_failed,
    a.is_simulated_error,
    a.n_items,
    a.avg_item_price,
    a.hour_of_day,
    a.day_of_week,
    a.days_since_last_order,
    a.client_avg_basket,
    a.amount_vs_avg_ratio,
    o.status          AS order_status,
    o.created_at      AS order_date
FROM anomalies a
JOIN users  u ON u.id = a.client_id
JOIN orders o ON o.id = a.order_id
WHERE a.run_id = (
    SELECT id FROM anomaly_runs
    WHERE status = 'success'
    ORDER BY finished_at DESC
    LIMIT 1
);
