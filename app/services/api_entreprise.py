"""
Service pour appeler l'API Recherche Entreprises (data.gouv.fr)
Documentation: https://recherche-entreprises.api.gouv.fr/docs

Limites: 7 requêtes/seconde par IP
"""

import requests
from functools import lru_cache
import time
import threading

API_BASE_URL = "https://recherche-entreprises.api.gouv.fr"
TIMEOUT = 10  # secondes
RATE_LIMIT = 7  # requêtes par seconde
RATE_INTERVAL = 1.0 / RATE_LIMIT  # ~0.143 seconde entre chaque requête

# Rate limiter simple
_last_request_time = 0
_rate_lock = threading.Lock()


def _rate_limit():
    """Applique le rate limiting pour respecter 7 req/sec"""
    global _last_request_time
    with _rate_lock:
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        if time_since_last < RATE_INTERVAL:
            time.sleep(RATE_INTERVAL - time_since_last)
        _last_request_time = time.time()


# Cache LRU pour éviter les requêtes répétées
@lru_cache(maxsize=1000)
def get_entreprise_data_cached(siren: str) -> dict | None:
    """Version cachée de get_entreprise_data"""
    return _fetch_entreprise_data(siren)


def get_entreprise_data(siren: str, use_cache: bool = True) -> dict | None:
    """
    Récupère les données complètes d'une entreprise depuis l'API.
    Inclut: dirigeants, finances, compléments.

    Args:
        siren: Numéro SIREN (9 chiffres)
        use_cache: Utiliser le cache LRU (défaut: True)

    Returns:
        dict avec les données ou None si erreur
    """
    if use_cache:
        return get_entreprise_data_cached(siren)
    return _fetch_entreprise_data(siren)


def _fetch_entreprise_data(siren: str) -> dict | None:
    """Fetch réel depuis l'API avec rate limiting"""
    try:
        _rate_limit()  # Respecter la limite de 7 req/sec

        response = requests.get(
            f"{API_BASE_URL}/search",
            params={"q": siren},
            timeout=TIMEOUT
        )
        response.raise_for_status()

        data = response.json()

        if data.get("results") and len(data["results"]) > 0:
            return data["results"][0]
        return None

    except requests.RequestException as e:
        print(f"Erreur API recherche-entreprises: {e}")
        return None


def get_bulk_entreprise_data(sirens: list, progress_callback=None) -> dict:
    """
    Récupère les données de plusieurs entreprises avec rate limiting.

    Args:
        sirens: Liste de SIREN
        progress_callback: Fonction callback(current, total) pour le suivi

    Returns:
        Dict {siren: data} pour chaque entreprise trouvée
    """
    results = {}
    total = len(sirens)

    for i, siren in enumerate(sirens):
        data = get_entreprise_data(siren, use_cache=True)
        if data:
            results[siren] = data

        if progress_callback:
            progress_callback(i + 1, total)

    return results


def get_dirigeants(siren: str) -> list:
    """
    Récupère la liste des dirigeants d'une entreprise.

    Returns:
        Liste de dirigeants avec leurs infos
    """
    data = get_entreprise_data(siren)
    if not data:
        return []

    dirigeants = data.get("dirigeants", [])

    # Formater les dirigeants
    result = []
    for d in dirigeants:
        if d.get("type_dirigeant") == "personne physique":
            result.append({
                "type": "Personne physique",
                "nom": d.get("nom", ""),
                "prenoms": d.get("prenoms", ""),
                "qualite": d.get("qualite", ""),
                "nationalite": d.get("nationalite", ""),
                "annee_naissance": d.get("annee_de_naissance", ""),
            })
        else:  # personne morale
            result.append({
                "type": "Personne morale",
                "siren": d.get("siren", ""),
                "denomination": d.get("denomination", ""),
                "qualite": d.get("qualite", ""),
            })

    return result


def get_finances(siren: str) -> dict:
    """
    Récupère les données financières d'une entreprise.

    Returns:
        Dict avec les données financières par année
    """
    data = get_entreprise_data(siren)
    if not data:
        return {}

    return data.get("finances", {})


def get_complements(siren: str) -> dict:
    """
    Récupère les informations complémentaires.

    Returns:
        Dict avec les compléments (ESS, qualiopi, etc.)
    """
    data = get_entreprise_data(siren)
    if not data:
        return {}

    return data.get("complements", {})
