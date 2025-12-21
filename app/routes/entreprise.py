from flask import Blueprint, render_template, jsonify, abort
from app.models import UniteLegale, Etablissement
from app import db

entreprise_bp = Blueprint('entreprise', __name__)


@entreprise_bp.route('/<siren>')
def detail(siren):
    """Page détail d'une entreprise"""
    # Validation SIREN
    if not siren.isdigit() or len(siren) != 9:
        abort(400, description="SIREN invalide")

    entreprise = db.session.query(UniteLegale).get(siren)
    if not entreprise:
        abort(404, description="Entreprise non trouvée")

    # Récupérer les établissements
    etablissements = db.session.query(Etablissement).filter_by(
        siren=siren
    ).order_by(
        Etablissement.etablissement_siege.desc(),  # Siège en premier
        Etablissement.etat_administratif.asc(),    # Actifs en premier
        Etablissement.date_creation.desc()
    ).all()

    # Séparer siège et autres établissements
    siege = None
    autres = []
    for etab in etablissements:
        if etab.est_siege:  # Utiliser la propriété qui gère TEXT 'true'/'false'
            siege = etab
        else:
            autres.append(etab)

    return render_template(
        'entreprise/detail.html',
        entreprise=entreprise,
        siege=siege,
        etablissements=autres,
        total_etablissements=len(etablissements)
    )


@entreprise_bp.route('/<siren>/json')
def detail_json(siren):
    """API JSON détail entreprise"""
    if not siren.isdigit() or len(siren) != 9:
        return jsonify({'error': 'SIREN invalide'}), 400

    entreprise = db.session.query(UniteLegale).get(siren)
    if not entreprise:
        return jsonify({'error': 'Entreprise non trouvée'}), 404

    # Récupérer les établissements
    etablissements = db.session.query(Etablissement).filter_by(
        siren=siren
    ).order_by(
        Etablissement.etablissement_siege.desc(),
        Etablissement.etat_administratif.asc()
    ).all()

    return jsonify({
        'entreprise': entreprise.to_dict(),
        'etablissements': [e.to_dict() for e in etablissements],
        'total_etablissements': len(etablissements)
    })


@entreprise_bp.route('/siret/<siret>')
def detail_by_siret(siret):
    """Redirection SIRET vers page entreprise"""
    if not siret.isdigit() or len(siret) != 14:
        abort(400, description="SIRET invalide")

    etab = db.session.query(Etablissement).get(siret)
    if not etab:
        abort(404, description="Établissement non trouvé")

    # Rediriger vers la page entreprise avec ancre sur l'établissement
    return render_template(
        'entreprise/detail.html',
        entreprise=etab.unite_legale,
        siege=db.session.query(Etablissement).filter_by(
            siren=etab.siren,
            etablissement_siege='true'
        ).first(),
        etablissements=db.session.query(Etablissement).filter(
            Etablissement.siren == etab.siren,
            Etablissement.etablissement_siege != 'true'
        ).all(),
        total_etablissements=db.session.query(Etablissement).filter_by(siren=etab.siren).count(),
        highlight_siret=siret
    )
