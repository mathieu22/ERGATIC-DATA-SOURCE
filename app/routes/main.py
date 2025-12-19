from flask import Blueprint, render_template
from app.models import UniteLegale, Etablissement
from app import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil avec recherche"""
    # Stats pour la page d'accueil
    stats = {
        'total_entreprises': db.session.query(UniteLegale).count(),
        'total_etablissements': db.session.query(Etablissement).count(),
        'entreprises_actives': db.session.query(UniteLegale).filter_by(etat_administratif='A').count(),
    }
    return render_template('index.html', stats=stats)


@main_bp.route('/stats')
def stats():
    """Page de statistiques"""
    stats = {
        'total_entreprises': db.session.query(UniteLegale).count(),
        'total_etablissements': db.session.query(Etablissement).count(),
        'entreprises_actives': db.session.query(UniteLegale).filter_by(etat_administratif='A').count(),
        'etablissements_actifs': db.session.query(Etablissement).filter_by(etat_administratif='A').count(),
    }
    return render_template('stats.html', stats=stats)
