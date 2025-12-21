-- ============================================
-- Materialized Views pour les filtres de recherche
-- ERGATIC-DATA-ENTERPRISE
-- ============================================

-- 1. Vue matérialisée des départements (codes postaux uniques)
DROP MATERIALIZED VIEW IF EXISTS mv_departements CASCADE;
CREATE MATERIALIZED VIEW mv_departements AS
SELECT DISTINCT
    substr(code_postal, 1, 2) AS code_departement
FROM etablissement
WHERE code_postal IS NOT NULL
  AND etablissement_siege = 'true'
  AND length(code_postal) >= 2
ORDER BY code_departement;

-- Index pour accès rapide
CREATE UNIQUE INDEX idx_mv_departements_code ON mv_departements(code_departement);

-- 2. Vue matérialisée des villes par département
DROP MATERIALIZED VIEW IF EXISTS mv_villes CASCADE;
CREATE MATERIALIZED VIEW mv_villes AS
SELECT DISTINCT
    substr(code_postal, 1, 2) AS code_departement,
    libelle_commune AS ville
FROM etablissement
WHERE libelle_commune IS NOT NULL
  AND code_postal IS NOT NULL
  AND etablissement_siege = 'true'
ORDER BY code_departement, ville;

-- Index pour recherche par département
CREATE INDEX idx_mv_villes_dept ON mv_villes(code_departement);
CREATE INDEX idx_mv_villes_ville ON mv_villes(ville);

-- 3. Vue matérialisée des codes NAF
DROP MATERIALIZED VIEW IF EXISTS mv_codes_naf CASCADE;
CREATE MATERIALIZED VIEW mv_codes_naf AS
SELECT DISTINCT
    activite_principale AS code_naf
FROM unite_legale
WHERE activite_principale IS NOT NULL
  AND etat_administratif = 'A'
ORDER BY code_naf;

-- Index unique
CREATE UNIQUE INDEX idx_mv_codes_naf_code ON mv_codes_naf(code_naf);

-- ============================================
-- Fonction pour rafraîchir toutes les vues
-- ============================================
CREATE OR REPLACE FUNCTION refresh_filter_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_departements;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_villes;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_codes_naf;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Vérification des vues créées
-- ============================================
SELECT
    schemaname,
    matviewname,
    ispopulated
FROM pg_matviews
WHERE matviewname LIKE 'mv_%';

-- Statistiques des vues
SELECT 'mv_departements' AS view_name, COUNT(*) AS nb_rows FROM mv_departements
UNION ALL
SELECT 'mv_villes', COUNT(*) FROM mv_villes
UNION ALL
SELECT 'mv_codes_naf', COUNT(*) FROM mv_codes_naf;
