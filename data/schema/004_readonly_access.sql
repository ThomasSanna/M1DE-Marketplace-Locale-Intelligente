-- =============================================================================
-- Marketplace Locale Intelligente - Acces SQL read-only
-- Auteur   : Yohann (DevOps/SRE)
-- Objectif : Mettre a disposition un acces SQL en lecture seule pour l'equipe
--            data (analyse/BI) sans risque de modification.
-- =============================================================================

DO
$$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_roles
        WHERE rolname = 'data_readonly'
    ) THEN
        CREATE ROLE data_readonly LOGIN PASSWORD 'change_me_data_readonly';
    END IF;
END
$$;

-- Acces a la base cible.
GRANT CONNECT ON DATABASE marketplace_db TO data_readonly;

-- Acces au schema applicatif.
GRANT USAGE ON SCHEMA public TO data_readonly;
REVOKE CREATE ON SCHEMA public FROM data_readonly;

-- Lecture sur tout l'existant (tables + vues + sequences).
GRANT SELECT ON ALL TABLES IN SCHEMA public TO data_readonly;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO data_readonly;

-- Lecture automatique sur les futurs objets.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO data_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO data_readonly;
