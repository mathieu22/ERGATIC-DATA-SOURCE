from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import or_, and_, func
from app.models import UniteLegale, Etablissement
from app import db

search_bp = Blueprint('search', __name__)


@search_bp.route('/')
def search_page():
    """Page de recherche avancée"""
    return render_template('search.html')


@search_bp.route('/api')
def search_api():
    """API de recherche d'entreprises"""
    # Paramètres de recherche
    q = request.args.get('q', '').strip()
    siren = request.args.get('siren', '').strip()
    siret = request.args.get('siret', '').strip()
    code_postal = request.args.get('code_postal', '').strip()
    ville = request.args.get('ville', '').strip()
    activite = request.args.get('activite', '').strip()
    categorie = request.args.get('categorie', '').strip()
    etat = request.args.get('etat', '').strip()

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    per_page = min(per_page, 100)  # Max 100 résultats par page

    # Construction de la requête
    query = db.session.query(UniteLegale)

    # Recherche par SIREN exact
    if siren:
        query = query.filter(UniteLegale.siren == siren)

    # Recherche par SIRET (via établissement)
    elif siret:
        etab = db.session.query(Etablissement).filter_by(siret=siret).first()
        if etab:
            query = query.filter(UniteLegale.siren == etab.siren)
        else:
            return jsonify({'results': [], 'total': 0, 'page': page, 'pages': 0})

    # Recherche textuelle
    elif q:
        search_term = f"%{q}%"
        query = query.filter(
            or_(
                UniteLegale.denomination.ilike(search_term),
                UniteLegale.sigle.ilike(search_term),
                UniteLegale.nom.ilike(search_term),
                UniteLegale.siren.like(search_term)
            )
        )

    # Filtres additionnels
    if activite:
        query = query.filter(UniteLegale.activite_principale.like(f"{activite}%"))

    if categorie:
        query = query.filter(UniteLegale.categorie_entreprise == categorie)

    if etat:
        query = query.filter(UniteLegale.etat_administratif == etat)

    # Filtre géographique (via établissement siège)
    if code_postal or ville:
        subquery = db.session.query(Etablissement.siren).filter(
            Etablissement.etablissement_siege == True
        )
        if code_postal:
            subquery = subquery.filter(Etablissement.code_postal.like(f"{code_postal}%"))
        if ville:
            subquery = subquery.filter(Etablissement.libelle_commune.ilike(f"%{ville}%"))
        query = query.filter(UniteLegale.siren.in_(subquery))

    # Tri par pertinence (entreprises actives d'abord)
    query = query.order_by(
        UniteLegale.etat_administratif.asc(),  # A avant C
        UniteLegale.denomination.asc()
    )

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Résultats avec info siège
    results = []
    for ul in pagination.items:
        data = ul.to_dict()
        # Récupérer info du siège
        siege = db.session.query(Etablissement).filter_by(
            siren=ul.siren,
            etablissement_siege=True
        ).first()
        if siege:
            data['siege'] = {
                'siret': siege.siret,
                'adresse': siege.adresse_ligne,
                'code_postal': siege.code_postal,
                'ville': siege.libelle_commune
            }
        results.append(data)

    return jsonify({
        'results': results,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'per_page': per_page
    })


@search_bp.route('/batch', methods=['POST'])
def search_batch():
    """Recherche par liste de SIREN"""
    data = request.get_json()
    sirens = data.get('sirens', [])

    if not sirens:
        return jsonify({'error': 'Liste de SIREN requise'}), 400

    # Nettoyer les SIREN
    sirens = [s.strip() for s in sirens if s.strip()]
    sirens = sirens[:1000]  # Limiter à 1000 SIREN

    # Recherche
    entreprises = db.session.query(UniteLegale).filter(
        UniteLegale.siren.in_(sirens)
    ).all()

    results = []
    for ul in entreprises:
        data = ul.to_dict()
        siege = db.session.query(Etablissement).filter_by(
            siren=ul.siren,
            etablissement_siege=True
        ).first()
        if siege:
            data['siege'] = siege.to_dict()
        results.append(data)

    # Identifier les SIREN non trouvés
    found_sirens = {ul.siren for ul in entreprises}
    not_found = [s for s in sirens if s not in found_sirens]

    return jsonify({
        'results': results,
        'total': len(results),
        'not_found': not_found,
        'not_found_count': len(not_found)
    })


@search_bp.route('/autocomplete')
def autocomplete():
    """Autocomplétion pour la recherche"""
    q = request.args.get('q', '').strip()

    if len(q) < 2:
        return jsonify([])

    # Recherche rapide
    results = db.session.query(
        UniteLegale.siren,
        UniteLegale.denomination
    ).filter(
        or_(
            UniteLegale.denomination.ilike(f"{q}%"),
            UniteLegale.siren.like(f"{q}%")
        ),
        UniteLegale.etat_administratif == 'A'
    ).limit(10).all()

    return jsonify([
        {'siren': r.siren, 'denomination': r.denomination}
        for r in results
    ])
