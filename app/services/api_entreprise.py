"""
Service pour appeler l'API Recherche Entreprises (data.gouv.fr)
Documentation: https://recherche-entreprises.api.gouv.fr/docs

Limites: 7 requêtes/seconde par IP
"""

import requests
from functools import lru_cache
import time

API_BASE_URL = "https://recherche-entreprises.api.gouv.fr"
TIMEOUT = 10  # secondes


def get_entreprise_data(siren: str) -> dict | None:
    """
    Récupère les données complètes d'une entreprise depuis l'API.
    Inclut: dirigeants, finances, compléments.

    Args:
        siren: Numéro SIREN (9 chiffres)

    Returns:
        dict avec les données ou None si erreur
    """
    try:
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
