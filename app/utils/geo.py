"""
Utilitaires de conversion de coordonnées géographiques
Lambert 93 (EPSG:2154) -> WGS84 GPS (EPSG:4326)
"""

try:
    from pyproj import Transformer
    PYPROJ_AVAILABLE = True
    # Créer le transformateur une seule fois (performance)
    transformer = Transformer.from_crs("EPSG:2154", "EPSG:4326", always_xy=True)
except ImportError:
    PYPROJ_AVAILABLE = False
    transformer = None


def lambert93_to_gps(x, y):
    """
    Convertit des coordonnées Lambert 93 en coordonnées GPS (lat, lon)

    Args:
        x: Coordonnée X Lambert 93 (abscisse)
        y: Coordonnée Y Lambert 93 (ordonnée)

    Returns:
        tuple: (latitude, longitude) ou (None, None) si conversion impossible
    """
    if not PYPROJ_AVAILABLE:
        return None, None

    if x is None or y is None:
        return None, None

    try:
        x = float(x)
        y = float(y)

        # Vérifier que les coordonnées sont dans la plage Lambert 93 France
        if not (100000 <= x <= 1300000 and 6000000 <= y <= 7200000):
            return None, None

        lon, lat = transformer.transform(x, y)
        return round(lat, 6), round(lon, 6)
    except (ValueError, TypeError):
        return None, None


def format_gps_link(lat, lon):
    """
    Génère un lien Google Maps pour les coordonnées GPS
    """
    if lat is None or lon is None:
        return None
    return f"https://www.google.com/maps?q={lat},{lon}"
