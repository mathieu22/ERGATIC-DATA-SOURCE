# PAPPERS - Base SIRENE

Application web pour explorer la base SIRENE des entreprises françaises.

## Stack technique

- **Backend** : Flask (Python)
- **Frontend** : Jinja2 + Tailwind CSS
- **Base de données** : PostgreSQL 16 (Docker)
- **Données** : Base SIRENE INSEE (~2 Go par fichier)

## Structure du projet

```
PAPPERS/
├── app/
│   ├── __init__.py           # Factory Flask
│   ├── models/               # Modèles SQLAlchemy
│   │   ├── unite_legale.py   # Entreprises
│   │   └── etablissement.py  # Établissements
│   ├── routes/               # Routes/Blueprints
│   │   ├── main.py           # Accueil, stats
│   │   ├── search.py         # Recherche + API
│   │   ├── entreprise.py     # Détail entreprise
│   │   └── export.py         # Exports CSV
│   └── templates/            # Templates Jinja2
├── scripts/
│   └── import_csv.py         # Script d'import
├── docs/
│   └── schema.sql            # Schéma PostgreSQL
├── docker-compose.yml        # Config Docker
├── requirements.txt          # Dépendances Python
└── run.py                    # Point d'entrée
```

## Installation

### 1. Prérequis

- Docker Desktop
- Python 3.10+
- Disque externe (1 To recommandé)

### 2. Préparer le disque externe

```bash
# Créer les dossiers sur le disque externe
mkdir -p "/Volumes/Crucial X10/pappers_data/postgres"
mkdir -p "/Volumes/Crucial X10/pappers_data/pgadmin"
```

### 3. Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer si nécessaire (mot de passe, etc.)
nano .env
```

### 4. Lancer PostgreSQL

```bash
# Démarrer les services
docker-compose up -d

# Vérifier le statut
docker-compose ps

# Voir les logs si problème
docker-compose logs postgres
```

### 5. Installer les dépendances Python

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 6. Télécharger les données SIRENE

Télécharger depuis [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/) :

- `StockUniteLegale_utf8.csv` (~2 Go)
- `StockEtablissement_utf8.csv` (~6 Go)

### 7. Importer les données

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Importer les unités légales (entreprises)
python scripts/import_csv.py -u /chemin/vers/StockUniteLegale_utf8.csv

# Importer les établissements
python scripts/import_csv.py -e /chemin/vers/StockEtablissement_utf8.csv

# Ou tout d'un coup si les fichiers sont dans le même dossier
python scripts/import_csv.py --all /chemin/vers/dossier/
```

**Durée estimée** : 10-30 minutes selon votre machine.

### 8. Lancer l'application

```bash
# Mode développement
python run.py

# Ou avec Flask CLI
flask run --host=0.0.0.0 --port=5000
```

L'application est accessible sur : http://localhost:5000

## Accès

| Service | URL | Identifiants |
|---------|-----|--------------|
| Application | http://localhost:5000 | - |
| PgAdmin | http://localhost:5050 | admin@pappers.local / admin123 |
| PostgreSQL | localhost:5432 | pappers / pappers_secure_2024 |

## Fonctionnalités

### Recherche
- Par nom d'entreprise
- Par SIREN (9 chiffres)
- Par SIRET (14 chiffres)
- Par localisation (code postal, ville)
- Par code NAF (activité)
- Par taille (PME, ETI, GE)
- Par statut (active/cessée)

### Recherche par liste
- Coller une liste de SIREN (un par ligne)
- Recherche batch jusqu'à 1000 SIREN

### Export
- Export CSV des résultats de recherche
- Export des établissements d'une entreprise

### Détail entreprise
- Informations légales complètes
- Liste des établissements
- Siège social mis en avant

## API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/search/api` | GET | Recherche d'entreprises |
| `/search/batch` | POST | Recherche par liste SIREN |
| `/search/autocomplete` | GET | Autocomplétion |
| `/entreprise/<siren>/json` | GET | Détail entreprise (JSON) |
| `/export/csv` | POST | Export CSV |
| `/export/search/csv` | GET | Export recherche CSV |

### Exemple recherche API

```
GET /search/api?q=TOTAL&etat=A&page=1&per_page=25
```

### Exemple recherche batch

```bash
curl -X POST http://localhost:5000/search/batch \
  -H "Content-Type: application/json" \
  -d '{"sirens": ["443061841", "552032534"]}'
```

## Production

### Avec Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Variables d'environnement production

```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=votre-clé-secrète-complexe
```

## Maintenance

### Mise à jour des données

```bash
# Télécharger les nouveaux fichiers
# Puis réimporter
python scripts/import_csv.py --all /chemin/vers/nouveaux/fichiers/
```

### Backup PostgreSQL

```bash
docker exec pappers_db pg_dump -U pappers sirene > backup.sql
```

### Restore

```bash
docker exec -i pappers_db psql -U pappers sirene < backup.sql
```

## Licence

Données SIRENE : Licence Ouverte (INSEE)
Code : MIT
# ERGATIC-DATA-SOURCE
