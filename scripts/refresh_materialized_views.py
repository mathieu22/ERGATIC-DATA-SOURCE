#!/usr/bin/env python3
"""
Script pour rafraîchir les vues matérialisées des filtres.
À exécuter après chaque import de données.

Usage:
    python scripts/refresh_materialized_views.py

Ou via cron (ex: tous les jours à 3h):
    0 3 * * * cd /path/to/project && python scripts/refresh_materialized_views.py
"""

import sys
import os
import time

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db


def refresh_views():
    """Rafraîchit les vues matérialisées des filtres."""
    app = create_app()

    with app.app_context():
        views = [
            'mv_departements',
            'mv_villes',
            'mv_codes_naf'
        ]

        for view in views:
            try:
                print(f"Rafraîchissement de {view}...", end=" ")
                start = time.time()

                # CONCURRENTLY permet de ne pas bloquer les lectures
                db.session.execute(
                    db.text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")
                )
                db.session.commit()

                elapsed = time.time() - start
                print(f"OK ({elapsed:.2f}s)")

            except Exception as e:
                print(f"ERREUR: {e}")
                db.session.rollback()

                # Si la vue n'existe pas, la créer
                if "does not exist" in str(e):
                    print(f"  -> Vue {view} non trouvée. Exécutez d'abord:")
                    print(f"     psql -d votre_db -f scripts/create_materialized_views.sql")

        # Afficher les statistiques
        print("\n--- Statistiques ---")
        for view in views:
            try:
                result = db.session.execute(
                    db.text(f"SELECT COUNT(*) FROM {view}")
                ).scalar()
                print(f"{view}: {result} entrées")
            except Exception:
                print(f"{view}: non disponible")


if __name__ == '__main__':
    refresh_views()
