# Quick Start - Test Local avec Mock Data

Guide pour tester l'interface PAPPERS en 5 minutes avec des données mock.

## Prérequis

- Docker Desktop installé et lancé
- Python 3.10+

## Installation rapide

### 1. Créer les dossiers

```bash
cd /Users/toky/Documents/SAMUEL/PAPPERS
mkdir -p data/postgres data/mock
```

### 2. Lancer PostgreSQL (local)

```bash
docker-compose -f docker-compose.local.yml up -d
```

Vérifier que c'est lancé :
```bash
docker-compose -f docker-compose.local.yml ps
```

### 3. Installer Python

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Générer les données mock

```bash
python scripts/generate_mock_data.py
```

Résultat :
```
GÉNÉRATION TERMINÉE !
Fichiers créés dans : data/mock
  - StockUniteLegale_mock.csv (1000 lignes)
  - StockEtablissement_mock.csv (~2500 lignes)
```

### 5. Importer les données mock

```bash
python scripts/import_csv.py --all data/mock/
```

### 6. Lancer l'application

```bash
python run.py
```

### 7. Ouvrir dans le navigateur

http://localhost:5000

## Commandes utiles

```bash
# Voir les logs PostgreSQL
docker-compose -f docker-compose.local.yml logs -f postgres

# Arrêter PostgreSQL
docker-compose -f docker-compose.local.yml down

# Redémarrer tout
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d

# Supprimer les données et recommencer
docker-compose -f docker-compose.local.yml down -v
rm -rf data/postgres
```

## En cas de problème

### "Connection refused"
```bash
# Vérifier que Docker tourne
docker ps

# Relancer PostgreSQL
docker-compose -f docker-compose.local.yml up -d
```

### "Database does not exist"
```bash
# Recréer la base
docker-compose -f docker-compose.local.yml down -v
rm -rf data/postgres
docker-compose -f docker-compose.local.yml up -d
# Attendre 10 secondes que le schéma se crée
sleep 10
python scripts/import_csv.py --all data/mock/
```

## Passer aux vraies données

Une fois l'interface validée, télécharger les vrais fichiers CSV depuis :
https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/

Puis utiliser `docker-compose.yml` (avec disque externe) au lieu de `docker-compose.local.yml`.
