#!/usr/bin/env python3
"""
Génère des données mock pour tester l'application PAPPERS
Crée des fichiers CSV avec ~1000 entreprises et ~3000 établissements
"""

import csv
import random
import os
from datetime import datetime, timedelta

# Dossier de sortie
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock')

# Données de référence
PRENOMS = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Michel', 'Anne', 'Philippe', 'Isabelle', 'François', 'Catherine']
NOMS = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau']
VILLES = [
    ('75001', 'PARIS 1', '75056'),
    ('75008', 'PARIS 8', '75056'),
    ('75011', 'PARIS 11', '75056'),
    ('69001', 'LYON 1', '69123'),
    ('69003', 'LYON 3', '69123'),
    ('13001', 'MARSEILLE 1', '13055'),
    ('33000', 'BORDEAUX', '33063'),
    ('31000', 'TOULOUSE', '31555'),
    ('44000', 'NANTES', '44109'),
    ('59000', 'LILLE', '59350'),
    ('67000', 'STRASBOURG', '67482'),
    ('06000', 'NICE', '06088'),
]
TYPES_VOIE = ['RUE', 'AVENUE', 'BOULEVARD', 'PLACE', 'IMPASSE', 'ALLEE']
NOMS_VOIE = ['DE LA REPUBLIQUE', 'VICTOR HUGO', 'JEAN JAURES', 'DE LA LIBERTE', 'DU GENERAL DE GAULLE',
             'PASTEUR', 'GAMBETTA', 'CARNOT', 'FOCH', 'DES FLEURS']
CODES_NAF = ['62.01Z', '70.22Z', '47.11F', '56.10A', '86.21Z', '43.21A', '68.20A', '96.02A', '85.59A', '46.90Z']
CATEGORIES_JURIDIQUES = ['1000', '5499', '5710', '5720', '5498']
CATEGORIES_ENTREPRISE = ['PME', 'ETI', 'GE', None, None, None]  # Plus de chances d'être None (petites entreprises)
TRANCHES_EFFECTIFS = ['00', '01', '02', '03', '11', '12', '21', '22', '31', '32']

DENOMINATIONS = [
    'TECH SOLUTIONS', 'DIGITAL SERVICES', 'CONSULTING EXPERTS', 'INNOVATION LAB',
    'DATA SYSTEMS', 'CLOUD FACTORY', 'WEB AGENCY', 'SMART BUSINESS', 'GLOBAL TRADE',
    'ECO SERVICES', 'PREMIUM CONSEIL', 'ALPHA TECH', 'BETA INDUSTRIES', 'GAMMA SOLUTIONS',
    'DELTA CONSULTING', 'OMEGA GROUP', 'SIGMA PARTNERS', 'EPSILON TECH', 'ZETA DIGITAL',
    'FRANCE IMPORT EXPORT', 'EURO LOGISTICS', 'MAISON DU CAFE', 'BOULANGERIE CENTRALE',
    'RESTAURANT LE GOURMET', 'HOTEL DE FRANCE', 'GARAGE CENTRAL', 'PHARMACIE DU CENTRE'
]


def random_date(start_year=1990, end_year=2023):
    """Génère une date aléatoire"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')


def generate_siren():
    """Génère un SIREN valide (9 chiffres)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(9)])


def generate_nic():
    """Génère un NIC (5 chiffres)"""
    return str(random.randint(10000, 99999))


def generate_unite_legale(siren, is_person=False):
    """Génère une unité légale (entreprise)"""
    date_creation = random_date(1990, 2020)

    data = {
        'siren': siren,
        'statutDiffusionUniteLegale': 'O',
        'unitePurgeeUniteLegale': '',
        'dateCreationUniteLegale': date_creation,
        'sigleUniteLegale': '',
        'sexeUniteLegale': '',
        'prenom1UniteLegale': '',
        'prenom2UniteLegale': '',
        'prenom3UniteLegale': '',
        'prenom4UniteLegale': '',
        'prenomUsuelUniteLegale': '',
        'pseudonymeUniteLegale': '',
        'identifiantAssociationUniteLegale': '',
        'trancheEffectifsUniteLegale': random.choice(TRANCHES_EFFECTIFS),
        'anneeEffectifsUniteLegale': '2022',
        'dateDernierTraitementUniteLegale': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'nombrePeriodesUniteLegale': '1',
        'categorieEntreprise': random.choice(CATEGORIES_ENTREPRISE) or '',
        'anneeCategorieEntreprise': '2022',
        'dateDebut': date_creation,
        'etatAdministratifUniteLegale': random.choice(['A', 'A', 'A', 'A', 'C']),  # 80% actives
        'nomUniteLegale': '',
        'nomUsageUniteLegale': '',
        'denominationUniteLegale': '',
        'denominationUsuelle1UniteLegale': '',
        'denominationUsuelle2UniteLegale': '',
        'denominationUsuelle3UniteLegale': '',
        'categorieJuridiqueUniteLegale': random.choice(CATEGORIES_JURIDIQUES),
        'activitePrincipaleUniteLegale': random.choice(CODES_NAF),
        'nomenclatureActivitePrincipaleUniteLegale': 'NAFRev2',
        'nicSiegeUniteLegale': '',  # Sera rempli après
        'economieSocialeSolidaireUniteLegale': random.choice(['O', 'N', '', '']),
        'societeMissionUniteLegale': random.choice(['O', 'N', '', '']),
        'caractereEmployeurUniteLegale': random.choice(['O', 'N']),
    }

    if is_person:
        data['sexeUniteLegale'] = random.choice(['M', 'F'])
        data['nomUniteLegale'] = random.choice(NOMS)
        data['prenom1UniteLegale'] = random.choice(PRENOMS)
        data['prenomUsuelUniteLegale'] = data['prenom1UniteLegale']
    else:
        base_name = random.choice(DENOMINATIONS)
        suffix = random.choice(['', ' SAS', ' SARL', ' SA', ' EURL', ' SCI'])
        data['denominationUniteLegale'] = f"{base_name}{suffix}"
        data['sigleUniteLegale'] = ''.join([w[0] for w in base_name.split()[:3]]) if random.random() > 0.7 else ''

    return data


def generate_etablissement(siren, nic, is_siege=False):
    """Génère un établissement"""
    ville = random.choice(VILLES)
    date_creation = random_date(1990, 2023)

    data = {
        'siren': siren,
        'nic': nic,
        'siret': f"{siren}{nic}",
        'statutDiffusionEtablissement': 'O',
        'dateCreationEtablissement': date_creation,
        'trancheEffectifsEtablissement': random.choice(TRANCHES_EFFECTIFS),
        'anneeEffectifsEtablissement': '2022',
        'activitePrincipaleRegistreMetiersEtablissement': '',
        'dateDernierTraitementEtablissement': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'etablissementSiege': 'true' if is_siege else 'false',
        'nombrePeriodesEtablissement': '1',
        'complementAdresseEtablissement': '',
        'numeroVoieEtablissement': str(random.randint(1, 150)),
        'indiceRepetitionEtablissement': '',
        'dernierNumeroVoieEtablissement': '',
        'indiceRepetitionDernierNumeroVoieEtablissement': '',
        'typeVoieEtablissement': random.choice(TYPES_VOIE),
        'libelleVoieEtablissement': random.choice(NOMS_VOIE),
        'codePostalEtablissement': ville[0],
        'libelleCommuneEtablissement': ville[1],
        'libelleCommuneEtrangerEtablissement': '',
        'distributionSpecialeEtablissement': '',
        'codeCommuneEtablissement': ville[2],
        'codeCedexEtablissement': '',
        'libelleCedexEtablissement': '',
        'codePaysEtrangerEtablissement': '',
        'libellePaysEtrangerEtablissement': '',
        'identifiantAdresseEtablissement': '',
        'coordonneeLambertAbscisseEtablissement': '',
        'coordonneeLambertOrdonneeEtablissement': '',
        'complementAdresse2Etablissement': '',
        'numeroVoie2Etablissement': '',
        'indiceRepetition2Etablissement': '',
        'typeVoie2Etablissement': '',
        'libelleVoie2Etablissement': '',
        'codePostal2Etablissement': '',
        'libelleCommune2Etablissement': '',
        'libelleCommuneEtranger2Etablissement': '',
        'distributionSpeciale2Etablissement': '',
        'codeCommune2Etablissement': '',
        'codeCedex2Etablissement': '',
        'libelleCedex2Etablissement': '',
        'codePaysEtranger2Etablissement': '',
        'libellePaysEtranger2Etablissement': '',
        'dateDebut': date_creation,
        'etatAdministratifEtablissement': 'A' if is_siege or random.random() > 0.2 else 'F',
        'enseigne1Etablissement': random.choice(['', '', '', f"Enseigne {random.randint(1, 100)}"]),
        'enseigne2Etablissement': '',
        'enseigne3Etablissement': '',
        'denominationUsuelleEtablissement': '',
        'activitePrincipaleEtablissement': random.choice(CODES_NAF),
        'nomenclatureActivitePrincipaleEtablissement': 'NAFRev2',
        'caractereEmployeurEtablissement': random.choice(['O', 'N']),
    }

    return data


def main():
    # Créer le dossier de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("="*60)
    print("GÉNÉRATION DES DONNÉES MOCK")
    print("="*60)

    # Générer les entreprises
    nb_entreprises = 1000
    unites_legales = []
    etablissements = []

    print(f"\nGénération de {nb_entreprises} entreprises...")

    for i in range(nb_entreprises):
        siren = generate_siren()
        is_person = random.random() < 0.3  # 30% personnes physiques

        ul = generate_unite_legale(siren, is_person)

        # Générer le siège
        nic_siege = generate_nic()
        ul['nicSiegeUniteLegale'] = nic_siege
        siege = generate_etablissement(siren, nic_siege, is_siege=True)
        etablissements.append(siege)

        # Générer des établissements secondaires (0 à 5)
        nb_etab = random.choices([0, 1, 2, 3, 4, 5], weights=[40, 30, 15, 8, 5, 2])[0]
        for _ in range(nb_etab):
            nic = generate_nic()
            etab = generate_etablissement(siren, nic, is_siege=False)
            etablissements.append(etab)

        unites_legales.append(ul)

        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{nb_entreprises} entreprises générées...")

    print(f"\nTotal: {len(unites_legales)} entreprises, {len(etablissements)} établissements")

    # Écrire le fichier des unités légales
    ul_file = os.path.join(OUTPUT_DIR, 'StockUniteLegale_mock.csv')
    print(f"\nÉcriture de {ul_file}...")

    with open(ul_file, 'w', newline='', encoding='utf-8') as f:
        if unites_legales:
            writer = csv.DictWriter(f, fieldnames=unites_legales[0].keys())
            writer.writeheader()
            writer.writerows(unites_legales)

    # Écrire le fichier des établissements
    etab_file = os.path.join(OUTPUT_DIR, 'StockEtablissement_mock.csv')
    print(f"Écriture de {etab_file}...")

    with open(etab_file, 'w', newline='', encoding='utf-8') as f:
        if etablissements:
            writer = csv.DictWriter(f, fieldnames=etablissements[0].keys())
            writer.writeheader()
            writer.writerows(etablissements)

    print("\n" + "="*60)
    print("GÉNÉRATION TERMINÉE !")
    print("="*60)
    print(f"\nFichiers créés dans : {OUTPUT_DIR}")
    print(f"  - StockUniteLegale_mock.csv ({len(unites_legales)} lignes)")
    print(f"  - StockEtablissement_mock.csv ({len(etablissements)} lignes)")


if __name__ == '__main__':
    main()
