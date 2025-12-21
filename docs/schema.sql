-- ============================================
-- SCHEMA SIRENE - Base de données entreprises
-- Projet PAPPERS
-- Version avec colonnes TEXT pour éviter les troncations
-- ============================================

-- Extension pour recherche floue (fuzzy search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Supprimer les vues et tables existantes
DROP VIEW IF EXISTS v_entreprise_complete CASCADE;
DROP TABLE IF EXISTS etablissement CASCADE;
DROP TABLE IF EXISTS unite_legale CASCADE;
DROP TABLE IF EXISTS ref_naf CASCADE;
DROP TABLE IF EXISTS ref_categorie_juridique CASCADE;

-- Table des unités légales (entreprises)
CREATE TABLE unite_legale (
    siren TEXT PRIMARY KEY,

    -- Identification
    denomination TEXT,
    denomination_usuelle_1 TEXT,
    denomination_usuelle_2 TEXT,
    denomination_usuelle_3 TEXT,
    sigle TEXT,

    -- Personne physique (si applicable)
    nom TEXT,
    nom_usage TEXT,
    prenom_1 TEXT,
    prenom_2 TEXT,
    prenom_3 TEXT,
    prenom_4 TEXT,
    prenom_usuel TEXT,
    pseudonyme TEXT,
    sexe TEXT,

    -- Caractéristiques
    categorie_juridique TEXT,
    activite_principale TEXT,
    nomenclature_activite TEXT,
    categorie_entreprise TEXT,
    tranche_effectifs TEXT,
    annee_effectifs TEXT,

    -- Statut
    etat_administratif TEXT,
    economie_sociale_solidaire TEXT,
    societe_mission TEXT,
    caractere_employeur TEXT,

    -- Dates
    date_creation TEXT,
    date_debut TEXT,
    date_dernier_traitement TEXT,

    -- Siège
    nic_siege TEXT,

    -- Autres
    identifiant_association TEXT,
    statut_diffusion TEXT,
    nombre_periodes TEXT,
    unite_purgee TEXT,
    annee_categorie_entreprise TEXT,

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des établissements
CREATE TABLE etablissement (
    siret TEXT PRIMARY KEY,
    siren TEXT NOT NULL,
    nic TEXT NOT NULL,

    -- Caractéristiques
    etablissement_siege TEXT,
    etat_administratif TEXT,
    activite_principale TEXT,
    nomenclature_activite TEXT,
    activite_registre_metiers TEXT,
    tranche_effectifs TEXT,
    annee_effectifs TEXT,
    caractere_employeur TEXT,

    -- Dénomination
    denomination_usuelle TEXT,
    enseigne_1 TEXT,
    enseigne_2 TEXT,
    enseigne_3 TEXT,

    -- Adresse principale
    numero_voie TEXT,
    indice_repetition TEXT,
    dernier_numero_voie TEXT,
    indice_repetition_dernier TEXT,
    type_voie TEXT,
    libelle_voie TEXT,
    complement_adresse TEXT,
    distribution_speciale TEXT,
    code_postal TEXT,
    libelle_commune TEXT,
    code_commune TEXT,
    code_cedex TEXT,
    libelle_cedex TEXT,

    -- Adresse à l'étranger
    code_pays_etranger TEXT,
    libelle_pays_etranger TEXT,
    libelle_commune_etranger TEXT,

    -- Adresse secondaire (si différente)
    numero_voie_2 TEXT,
    indice_repetition_2 TEXT,
    type_voie_2 TEXT,
    libelle_voie_2 TEXT,
    complement_adresse_2 TEXT,
    distribution_speciale_2 TEXT,
    code_postal_2 TEXT,
    libelle_commune_2 TEXT,
    code_commune_2 TEXT,
    code_cedex_2 TEXT,
    libelle_cedex_2 TEXT,
    code_pays_etranger_2 TEXT,
    libelle_pays_etranger_2 TEXT,
    libelle_commune_etranger_2 TEXT,

    -- Géolocalisation
    coordonnee_lambert_x TEXT,
    coordonnee_lambert_y TEXT,
    identifiant_adresse TEXT,

    -- Dates
    date_creation TEXT,
    date_debut TEXT,
    date_dernier_traitement TEXT,

    -- Autres
    statut_diffusion TEXT,
    nombre_periodes TEXT,

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEX pour optimiser les recherches
-- ============================================

-- Index sur unite_legale
CREATE INDEX idx_ul_denomination ON unite_legale(denomination);
CREATE INDEX idx_ul_denomination_trgm ON unite_legale USING gin(denomination gin_trgm_ops);
CREATE INDEX idx_ul_activite ON unite_legale(activite_principale);
CREATE INDEX idx_ul_categorie_juridique ON unite_legale(categorie_juridique);
CREATE INDEX idx_ul_categorie_entreprise ON unite_legale(categorie_entreprise);
CREATE INDEX idx_ul_etat ON unite_legale(etat_administratif);
CREATE INDEX idx_ul_tranche_effectifs ON unite_legale(tranche_effectifs);

-- Index sur etablissement
CREATE INDEX idx_etab_siren ON etablissement(siren);
CREATE INDEX idx_etab_siege ON etablissement(etablissement_siege);
CREATE INDEX idx_etab_etat ON etablissement(etat_administratif);
CREATE INDEX idx_etab_activite ON etablissement(activite_principale);
CREATE INDEX idx_etab_code_postal ON etablissement(code_postal);
CREATE INDEX idx_etab_commune ON etablissement(libelle_commune);
CREATE INDEX idx_etab_code_commune ON etablissement(code_commune);
CREATE INDEX idx_etab_denomination ON etablissement(denomination_usuelle);

-- Index composite pour recherches fréquentes
CREATE INDEX idx_etab_siren_siege ON etablissement(siren, etablissement_siege);
CREATE INDEX idx_etab_cp_activite ON etablissement(code_postal, activite_principale);

-- ============================================
-- Vue pour faciliter les requêtes
-- ============================================
CREATE VIEW v_entreprise_complete AS
SELECT
    ul.siren,
    ul.denomination,
    ul.sigle,
    ul.categorie_juridique,
    ul.activite_principale AS activite_principale_ul,
    ul.categorie_entreprise,
    ul.tranche_effectifs AS tranche_effectifs_ul,
    ul.etat_administratif AS etat_ul,
    ul.date_creation AS date_creation_ul,
    -- Siège
    e.siret AS siret_siege,
    e.denomination_usuelle AS denomination_siege,
    CONCAT(e.numero_voie, ' ', COALESCE(e.type_voie, ''), ' ', COALESCE(e.libelle_voie, '')) AS adresse_siege,
    e.code_postal AS cp_siege,
    e.libelle_commune AS ville_siege,
    e.activite_principale AS activite_siege,
    e.etat_administratif AS etat_siege
FROM unite_legale ul
LEFT JOIN etablissement e ON ul.siren = e.siren AND e.etablissement_siege = 'true';

-- ============================================
-- Table de référence des codes NAF (à remplir)
-- ============================================
CREATE TABLE ref_naf (
    code TEXT PRIMARY KEY,
    libelle TEXT,
    section TEXT,
    libelle_section TEXT
);

-- ============================================
-- Table de référence des catégories juridiques
-- ============================================
CREATE TABLE ref_categorie_juridique (
    code TEXT PRIMARY KEY,
    libelle TEXT
);
