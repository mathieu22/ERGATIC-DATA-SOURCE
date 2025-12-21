#!/usr/bin/env python3
"""
Script d'import des fichiers CSV SIRENE dans PostgreSQL
Optimisé pour fichiers volumineux (2+ Go) avec gestion mémoire
Compatible psycopg3

Usage:
    python scripts/import_csv_v3.py --unite-legale /chemin/vers/StockUniteLegale.csv
    python scripts/import_csv_v3.py --etablissement /chemin/vers/StockEtablissement.csv
    python scripts/import_csv_v3.py --all /chemin/vers/dossier/
"""

import os
import sys
import argparse
import time
import mmap
import gc
import psycopg
from psycopg import sql
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', '5433'),
    'dbname': os.getenv('POSTGRES_DB', 'sirene'),
    'user': os.getenv('POSTGRES_USER', 'pappers'),
    'password': os.getenv('POSTGRES_PASSWORD', 'pappers_secure_2024')
}

print(DB_CONFIG)

# Taille des chunks pour lecture (64 Mo)
CHUNK_SIZE = 64 * 1024 * 1024

# Mapping des colonnes CSV vers colonnes DB
UNITE_LEGALE_MAPPING = {
    'siren': 'siren',
    'denominationUniteLegale': 'denomination',
    'denominationUsuelle1UniteLegale': 'denomination_usuelle_1',
    'denominationUsuelle2UniteLegale': 'denomination_usuelle_2',
    'denominationUsuelle3UniteLegale': 'denomination_usuelle_3',
    'sigleUniteLegale': 'sigle',
    'nomUniteLegale': 'nom',
    'nomUsageUniteLegale': 'nom_usage',
    'prenom1UniteLegale': 'prenom_1',
    'prenom2UniteLegale': 'prenom_2',
    'prenom3UniteLegale': 'prenom_3',
    'prenom4UniteLegale': 'prenom_4',
    'prenomUsuelUniteLegale': 'prenom_usuel',
    'pseudonymeUniteLegale': 'pseudonyme',
    'sexeUniteLegale': 'sexe',
    'categorieJuridiqueUniteLegale': 'categorie_juridique',
    'activitePrincipaleUniteLegale': 'activite_principale',
    'nomenclatureActivitePrincipaleUniteLegale': 'nomenclature_activite',
    'categorieEntreprise': 'categorie_entreprise',
    'trancheEffectifsUniteLegale': 'tranche_effectifs',
    'anneeEffectifsUniteLegale': 'annee_effectifs',
    'etatAdministratifUniteLegale': 'etat_administratif',
    'economieSocialeSolidaireUniteLegale': 'economie_sociale_solidaire',
    'societeMissionUniteLegale': 'societe_mission',
    'caractereEmployeurUniteLegale': 'caractere_employeur',
    'dateCreationUniteLegale': 'date_creation',
    'dateDebut': 'date_debut',
    'dateDernierTraitementUniteLegale': 'date_dernier_traitement',
    'nicSiegeUniteLegale': 'nic_siege',
    'identifiantAssociationUniteLegale': 'identifiant_association',
    'statutDiffusionUniteLegale': 'statut_diffusion',
    'nombrePeriodesUniteLegale': 'nombre_periodes',
    'unitePurgeeUniteLegale': 'unite_purgee',
    'anneeCategorieEntreprise': 'annee_categorie_entreprise'
}

ETABLISSEMENT_MAPPING = {
    'siret': 'siret',
    'siren': 'siren',
    'nic': 'nic',
    'etablissementSiege': 'etablissement_siege',
    'etatAdministratifEtablissement': 'etat_administratif',
    'activitePrincipaleEtablissement': 'activite_principale',
    'nomenclatureActivitePrincipaleEtablissement': 'nomenclature_activite',
    'activitePrincipaleRegistreMetiersEtablissement': 'activite_registre_metiers',
    'trancheEffectifsEtablissement': 'tranche_effectifs',
    'anneeEffectifsEtablissement': 'annee_effectifs',
    'caractereEmployeurEtablissement': 'caractere_employeur',
    'denominationUsuelleEtablissement': 'denomination_usuelle',
    'enseigne1Etablissement': 'enseigne_1',
    'enseigne2Etablissement': 'enseigne_2',
    'enseigne3Etablissement': 'enseigne_3',
    'numeroVoieEtablissement': 'numero_voie',
    'indiceRepetitionEtablissement': 'indice_repetition',
    'dernierNumeroVoieEtablissement': 'dernier_numero_voie',
    'indiceRepetitionDernierNumeroVoieEtablissement': 'indice_repetition_dernier',
    'typeVoieEtablissement': 'type_voie',
    'libelleVoieEtablissement': 'libelle_voie',
    'complementAdresseEtablissement': 'complement_adresse',
    'distributionSpecialeEtablissement': 'distribution_speciale',
    'codePostalEtablissement': 'code_postal',
    'libelleCommuneEtablissement': 'libelle_commune',
    'codeCommuneEtablissement': 'code_commune',
    'codeCedexEtablissement': 'code_cedex',
    'libelleCedexEtablissement': 'libelle_cedex',
    'codePaysEtrangerEtablissement': 'code_pays_etranger',
    'libellePaysEtrangerEtablissement': 'libelle_pays_etranger',
    'libelleCommuneEtrangerEtablissement': 'libelle_commune_etranger',
    'numeroVoie2Etablissement': 'numero_voie_2',
    'indiceRepetition2Etablissement': 'indice_repetition_2',
    'typeVoie2Etablissement': 'type_voie_2',
    'libelleVoie2Etablissement': 'libelle_voie_2',
    'complementAdresse2Etablissement': 'complement_adresse_2',
    'distributionSpeciale2Etablissement': 'distribution_speciale_2',
    'codePostal2Etablissement': 'code_postal_2',
    'libelleCommune2Etablissement': 'libelle_commune_2',
    'codeCommune2Etablissement': 'code_commune_2',
    'codeCedex2Etablissement': 'code_cedex_2',
    'libelleCedex2Etablissement': 'libelle_cedex_2',
    'codePaysEtranger2Etablissement': 'code_pays_etranger_2',
    'libellePaysEtranger2Etablissement': 'libelle_pays_etranger_2',
    'libelleCommuneEtranger2Etablissement': 'libelle_commune_etranger_2',
    'coordonneeLambertAbscisseEtablissement': 'coordonnee_lambert_x',
    'coordonneeLambertOrdonneeEtablissement': 'coordonnee_lambert_y',
    'identifiantAdresseEtablissement': 'identifiant_adresse',
    'dateCreationEtablissement': 'date_creation',
    'dateDebut': 'date_debut',
    'dateDernierTraitementEtablissement': 'date_dernier_traitement',
    'statutDiffusionEtablissement': 'statut_diffusion',
    'nombrePeriodesEtablissement': 'nombre_periodes'
}


def get_file_size(filepath):
    """Retourne la taille du fichier en bytes"""
    return os.path.getsize(filepath)


def format_size(bytes_size):
    """Formate la taille en unité lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def format_time(seconds):
    """Formate le temps en format lisible"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        return f"{seconds//60:.0f}m {seconds%60:.0f}s"
    else:
        return f"{seconds//3600:.0f}h {(seconds%3600)//60:.0f}m"


def print_progress(current, total, start_time, prefix=""):
    """Affiche une barre de progression"""
    elapsed = time.time() - start_time
    percent = (current / total) * 100 if total > 0 else 0
    rate = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / rate if rate > 0 else 0

    bar_length = 30
    filled = int(bar_length * current / total) if total > 0 else 0
    bar = '=' * filled + '-' * (bar_length - filled)

    sys.stdout.write(f'\r{prefix}[{bar}] {percent:.1f}% | {format_size(current)}/{format_size(total)} | {format_size(rate)}/s | ETA: {format_time(eta)}  ')
    sys.stdout.flush()


def get_connection():
    """Crée une connexion à la base de données"""
    conn = psycopg.connect(**DB_CONFIG)
    conn.autocommit = False
    return conn


def prepare_database(cursor, table_name):
    """Prépare la base pour l'import (désactive contraintes temporairement)"""
    print("Préparation de la base de données...")

    # Désactiver les triggers et contraintes temporairement
    cursor.execute(f"ALTER TABLE {table_name} DISABLE TRIGGER ALL")

    # Vider la table
    cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")


def restore_database(cursor, table_name):
    """Restaure les contraintes après import"""
    print("\nRestauration des contraintes...")
    cursor.execute(f"ALTER TABLE {table_name} ENABLE TRIGGER ALL")


def import_csv_streaming(filepath, table_name, mapping):
    """
    Import CSV avec streaming - utilise PostgreSQL COPY via psycopg3
    """
    file_size = get_file_size(filepath)

    print(f"\n{'='*70}")
    print(f"IMPORT CSV STREAMING (psycopg3)")
    print(f"{'='*70}")
    print(f"Fichier     : {filepath}")
    print(f"Taille      : {format_size(file_size)}")
    print(f"Table cible : {table_name}")
    print(f"{'='*70}\n")

    start_time = time.time()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Préparation
        prepare_database(cursor, table_name)
        conn.commit()

        # Colonnes DB dans l'ordre du mapping
        db_columns = list(mapping.values())
        columns_str = ', '.join(db_columns)

        print("Import en cours (streaming)...")
        print("Cela peut prendre plusieurs minutes pour les gros fichiers.\n")

        # Utiliser COPY avec psycopg3
        with open(filepath, 'r', encoding='utf-8') as f:
            # Psycopg3 utilise copy() avec un context manager
            with cursor.copy(f"COPY {table_name} ({columns_str}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',', NULL '')") as copy:
                bytes_read = 0
                last_update = 0

                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    copy.write(chunk.encode('utf-8'))
                    bytes_read += len(chunk)

                    # Mise à jour progress tous les 1%
                    if bytes_read - last_update > file_size * 0.01:
                        print_progress(bytes_read, file_size, start_time, "Import: ")
                        last_update = bytes_read

        print()  # Nouvelle ligne après progress bar

        # Commit
        print("Validation des données...")
        conn.commit()

        # Compter les résultats
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]

        # Restaurer contraintes
        restore_database(cursor, table_name)
        conn.commit()

        # Stats finales
        elapsed = time.time() - start_time
        rate = count / elapsed if elapsed > 0 else 0

        print(f"\n{'='*70}")
        print(f"IMPORT TERMINÉ AVEC SUCCÈS")
        print(f"{'='*70}")
        print(f"Lignes importées : {count:,}")
        print(f"Durée totale     : {format_time(elapsed)}")
        print(f"Vitesse          : {rate:,.0f} lignes/seconde")
        print(f"{'='*70}\n")

        return count

    except Exception as e:
        conn.rollback()
        print(f"\n\nERREUR : {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        gc.collect()


def import_csv_chunked(filepath, table_name, mapping, chunk_lines=50000):
    """
    Import CSV par chunks - fallback si COPY échoue
    """
    import csv

    file_size = get_file_size(filepath)

    print(f"\n{'='*70}")
    print(f"IMPORT CSV PAR CHUNKS (psycopg3)")
    print(f"{'='*70}")
    print(f"Fichier      : {filepath}")
    print(f"Taille       : {format_size(file_size)}")
    print(f"Table cible  : {table_name}")
    print(f"Taille chunk : {chunk_lines:,} lignes")
    print(f"{'='*70}\n")

    start_time = time.time()
    total_rows = 0

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Préparation
        prepare_database(cursor, table_name)
        conn.commit()

        db_columns = list(mapping.values())
        csv_columns = list(mapping.keys())

        # Préparer l'INSERT
        placeholders = ', '.join(['%s'] * len(db_columns))
        insert_sql = f"""
            INSERT INTO {table_name} ({', '.join(db_columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """

        print("Import par chunks en cours...\n")

        with open(filepath, 'r', encoding='utf-8', buffering=CHUNK_SIZE) as f:
            reader = csv.reader(f)
            header = next(reader)

            # Mapping index -> colonne
            col_indices = {}
            for csv_col in csv_columns:
                try:
                    col_indices[csv_col] = header.index(csv_col)
                except ValueError:
                    col_indices[csv_col] = None

            batch = []
            bytes_read = len(','.join(header))

            for row in reader:
                values = []
                for csv_col in csv_columns:
                    idx = col_indices.get(csv_col)
                    if idx is not None and idx < len(row):
                        val = row[idx]
                        values.append(val if val else None)
                    else:
                        values.append(None)

                batch.append(tuple(values))
                total_rows += 1
                bytes_read += sum(len(c) for c in row) + len(row)

                if len(batch) >= chunk_lines:
                    cursor.executemany(insert_sql, batch)
                    conn.commit()

                    print_progress(bytes_read, file_size, start_time,
                                   f"Import ({total_rows:,} lignes): ")

                    batch = []
                    gc.collect()

            if batch:
                cursor.executemany(insert_sql, batch)
                conn.commit()

        print()

        restore_database(cursor, table_name)
        conn.commit()

        elapsed = time.time() - start_time
        rate = total_rows / elapsed if elapsed > 0 else 0

        print(f"\n{'='*70}")
        print(f"IMPORT TERMINÉ AVEC SUCCÈS")
        print(f"{'='*70}")
        print(f"Lignes importées : {total_rows:,}")
        print(f"Durée totale     : {format_time(elapsed)}")
        print(f"Vitesse          : {rate:,.0f} lignes/seconde")
        print(f"{'='*70}\n")

        return total_rows

    except Exception as e:
        conn.rollback()
        print(f"\n\nERREUR : {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        gc.collect()


def create_indexes(verbose=True):
    """Crée les index après l'import"""
    if verbose:
        print("\n" + "="*70)
        print("CRÉATION DES INDEX")
        print("="*70 + "\n")

    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    indexes = [
        ('idx_ul_denomination', 'unite_legale', 'denomination'),
        ('idx_ul_activite', 'unite_legale', 'activite_principale'),
        ('idx_ul_categorie_juridique', 'unite_legale', 'categorie_juridique'),
        ('idx_ul_categorie_entreprise', 'unite_legale', 'categorie_entreprise'),
        ('idx_ul_etat', 'unite_legale', 'etat_administratif'),
        ('idx_ul_tranche_effectifs', 'unite_legale', 'tranche_effectifs'),
        ('idx_etab_siren', 'etablissement', 'siren'),
        ('idx_etab_siege', 'etablissement', 'etablissement_siege'),
        ('idx_etab_etat', 'etablissement', 'etat_administratif'),
        ('idx_etab_activite', 'etablissement', 'activite_principale'),
        ('idx_etab_code_postal', 'etablissement', 'code_postal'),
        ('idx_etab_commune', 'etablissement', 'libelle_commune'),
        ('idx_etab_code_commune', 'etablissement', 'code_commune'),
    ]

    try:
        for i, (idx_name, table, column) in enumerate(indexes, 1):
            if verbose:
                print(f"  [{i}/{len(indexes)}] Création de {idx_name}...")
            cursor.execute(f'DROP INDEX IF EXISTS {idx_name}')
            cursor.execute(f'CREATE INDEX CONCURRENTLY IF NOT EXISTS {idx_name} ON {table}({column})')

        if verbose:
            print(f"  Création des index composites...")

        cursor.execute('DROP INDEX IF EXISTS idx_etab_siren_siege')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_etab_siren_siege ON etablissement(siren, etablissement_siege)')

        if verbose:
            print("\nIndex créés avec succès !")

    finally:
        cursor.close()
        conn.close()


def analyze_tables(verbose=True):
    """Met à jour les statistiques des tables"""
    if verbose:
        print("\nMise à jour des statistiques (ANALYZE)...")

    conn = get_connection()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        cursor.execute('ANALYZE unite_legale')
        cursor.execute('ANALYZE etablissement')
        if verbose:
            print("Statistiques mises à jour !")
    finally:
        cursor.close()
        conn.close()


def check_database_connection():
    """Vérifie la connexion à la base de données"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"ERREUR de connexion à la base de données : {e}")
        print("\nVérifiez que :")
        print("  1. Docker est lancé")
        print("  2. Le conteneur PostgreSQL est démarré (docker-compose up -d)")
        print("  3. Les variables d'environnement dans .env sont correctes")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Import des fichiers CSV SIRENE dans PostgreSQL (psycopg3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python import_csv_v3.py -u /chemin/vers/StockUniteLegale_utf8.csv
  python import_csv_v3.py -e /chemin/vers/StockEtablissement_utf8.csv
  python import_csv_v3.py --all /chemin/vers/dossier/
  python import_csv_v3.py -u fichier.csv --method chunked
        """
    )

    parser.add_argument('--unite-legale', '-u', help='Chemin vers StockUniteLegale.csv')
    parser.add_argument('--etablissement', '-e', help='Chemin vers StockEtablissement.csv')
    parser.add_argument('--all', '-a', help='Dossier contenant les deux fichiers CSV')
    parser.add_argument('--method', '-m', choices=['streaming', 'chunked'], default='chunked',
                        help='Méthode d\'import (streaming=COPY, chunked=par lots)')
    parser.add_argument('--chunk-size', '-c', type=int, default=50000,
                        help='Nombre de lignes par chunk (défaut: 50000)')
    parser.add_argument('--no-index', action='store_true', help='Ne pas créer les index après import')
    parser.add_argument('--index-only', action='store_true', help='Créer uniquement les index')

    args = parser.parse_args()

    print("Vérification de la connexion à PostgreSQL...")
    if not check_database_connection():
        sys.exit(1)
    print("Connexion OK !\n")

    if args.index_only:
        create_indexes()
        analyze_tables()
        sys.exit(0)

    if args.all:
        folder = args.all
        if not os.path.isdir(folder):
            print(f"ERREUR : Le dossier n'existe pas : {folder}")
            sys.exit(1)

        for f in os.listdir(folder):
            fl = f.lower()
            if 'unitelegale' in fl and fl.endswith('.csv'):
                args.unite_legale = os.path.join(folder, f)
                print(f"Trouvé : {args.unite_legale}")
            elif 'etablissement' in fl and fl.endswith('.csv'):
                args.etablissement = os.path.join(folder, f)
                print(f"Trouvé : {args.etablissement}")

    if args.method == 'streaming':
        import_func = import_csv_streaming
    else:
        import_func = lambda fp, tn, mp: import_csv_chunked(fp, tn, mp, args.chunk_size)

    if args.unite_legale:
        if not os.path.exists(args.unite_legale):
            print(f"ERREUR : Fichier non trouvé : {args.unite_legale}")
            sys.exit(1)
        import_func(args.unite_legale, 'unite_legale', UNITE_LEGALE_MAPPING)

    if args.etablissement:
        if not os.path.exists(args.etablissement):
            print(f"ERREUR : Fichier non trouvé : {args.etablissement}")
            sys.exit(1)
        import_func(args.etablissement, 'etablissement', ETABLISSEMENT_MAPPING)

    if not args.no_index and (args.unite_legale or args.etablissement):
        create_indexes()
        analyze_tables()

    if args.unite_legale or args.etablissement:
        print("\n" + "="*70)
        print("IMPORT COMPLET TERMINÉ !")
        print("="*70)
        print("\nVous pouvez maintenant lancer l'application :")
        print("  python run.py")
        print("\nPuis ouvrir : http://localhost:5000")


if __name__ == '__main__':
    main()
