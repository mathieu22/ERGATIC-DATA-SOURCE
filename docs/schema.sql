-- ============================================
-- SCHEMA SIRENE - Base de données entreprises
-- Projet PAPPERS
-- ============================================

-- Table des unités légales (entreprises)
CREATE TABLE unite_legale (
    siren VARCHAR(9) PRIMARY KEY,

    -- Identification
    denomination VARCHAR(255),
    denomination_usuelle_1 VARCHAR(255),
    denomination_usuelle_2 VARCHAR(255),
    denomination_usuelle_3 VARCHAR(255),
    sigle VARCHAR(50),

    -- Personne physique (si applicable)
    nom VARCHAR(100),
    nom_usage VARCHAR(100),
    prenom_1 VARCHAR(100),
    prenom_2 VARCHAR(100),
    prenom_3 VARCHAR(100),
    prenom_4 VARCHAR(100),
    prenom_usuel VARCHAR(100),
    pseudonyme VARCHAR(100),
    sexe CHAR(1),

    -- Caractéristiques
    categorie_juridique VARCHAR(10),
    activite_principale VARCHAR(10),
    nomenclature_activite VARCHAR(10),
    categorie_entreprise VARCHAR(5),       -- PME, ETI, GE
    tranche_effectifs VARCHAR(5),
    annee_effectifs INTEGER,

    -- Statut
    etat_administratif CHAR(1),            -- A=Actif, C=Cessé
    economie_sociale_solidaire CHAR(1),
    societe_mission CHAR(1),
    caractere_employeur CHAR(1),

    -- Dates
    date_creation DATE,
    date_debut DATE,
    date_dernier_traitement TIMESTAMP,

    -- Siège
    nic_siege VARCHAR(5),

    -- Autres
    identifiant_association VARCHAR(20),
    statut_diffusion CHAR(1),
    nombre_periodes INTEGER,
    unite_purgee CHAR(1),
    annee_categorie_entreprise INTEGER,

    -- Métadonnées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des établissements
CREATE TABLE etablissement (
    siret VARCHAR(14) PRIMARY KEY,
    siren VARCHAR(9) NOT NULL REFERENCES unite_legale(siren),
    nic VARCHAR(5) NOT NULL,

    -- Caractéristiques
    etablissement_siege BOOLEAN,
    etat_administratif CHAR(1),            -- A=Actif, F=Fermé
    activite_principale VARCHAR(10),
    nomenclature_activite VARCHAR(10),
    activite_registre_metiers VARCHAR(10),
    tranche_effectifs VARCHAR(5),
    annee_effectifs INTEGER,
    caractere_employeur CHAR(1),

    -- Dénomination
    denomination_usuelle VARCHAR(255),
    enseigne_1 VARCHAR(255),
    enseigne_2 VARCHAR(255),
    enseigne_3 VARCHAR(255),

    -- Adresse principale
    numero_voie VARCHAR(10),
    indice_repetition VARCHAR(5),
    dernier_numero_voie VARCHAR(10),
    indice_repetition_dernier VARCHAR(5),
    type_voie VARCHAR(10),
    libelle_voie VARCHAR(255),
    complement_adresse VARCHAR(255),
    distribution_speciale VARCHAR(100),
    code_postal VARCHAR(10),
    libelle_commune VARCHAR(100),
    code_commune VARCHAR(10),
    code_cedex VARCHAR(10),
    libelle_cedex VARCHAR(100),

    -- Adresse à l'étranger
    code_pays_etranger VARCHAR(10),
    libelle_pays_etranger VARCHAR(100),
    libelle_commune_etranger VARCHAR(100),

    -- Adresse secondaire (si différente)
    numero_voie_2 VARCHAR(10),
    indice_repetition_2 VARCHAR(5),
    type_voie_2 VARCHAR(10),
    libelle_voie_2 VARCHAR(255),
    complement_adresse_2 VARCHAR(255),
    distribution_speciale_2 VARCHAR(100),
    code_postal_2 VARCHAR(10),
    libelle_commune_2 VARCHAR(100),
    code_commune_2 VARCHAR(10),
    code_cedex_2 VARCHAR(10),
    libelle_cedex_2 VARCHAR(100),
    code_pays_etranger_2 VARCHAR(10),
    libelle_pays_etranger_2 VARCHAR(100),
    libelle_commune_etranger_2 VARCHAR(100),

    -- Géolocalisation
    coordonnee_lambert_x DECIMAL(15, 2),
    coordonnee_lambert_y DECIMAL(15, 2),
    identifiant_adresse VARCHAR(50),

    -- Dates
    date_creation DATE,
    date_debut DATE,
    date_dernier_traitement TIMESTAMP,

    -- Autres
    statut_diffusion CHAR(1),
    nombre_periodes INTEGER,

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
-- Extension pour recherche floue (fuzzy search)
-- ============================================
CREATE EXTENSION IF NOT EXISTS pg_trgm;

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
    e.numero_voie || ' ' || COALESCE(e.type_voie, '') || ' ' || COALESCE(e.libelle_voie, '') AS adresse_siege,
    e.code_postal AS cp_siege,
    e.libelle_commune AS ville_siege,
    e.activite_principale AS activite_siege,
    e.etat_administratif AS etat_siege
FROM unite_legale ul
LEFT JOIN etablissement e ON ul.siren = e.siren AND e.etablissement_siege = true;

-- ============================================
-- Table de référence des codes NAF (à remplir)
-- ============================================
CREATE TABLE ref_naf (
    code VARCHAR(10) PRIMARY KEY,
    libelle VARCHAR(255),
    section VARCHAR(5),
    libelle_section VARCHAR(100)
);

-- ============================================
-- Table de référence des catégories juridiques
-- ============================================
CREATE TABLE ref_categorie_juridique (
    code VARCHAR(10) PRIMARY KEY,
    libelle VARCHAR(255)
);
