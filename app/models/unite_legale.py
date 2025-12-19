from app import db


class UniteLegale(db.Model):
    """Modèle pour les unités légales (entreprises)"""
    __tablename__ = 'unite_legale'

    siren = db.Column(db.String(9), primary_key=True)

    # Identification
    denomination = db.Column(db.String(255), index=True)
    denomination_usuelle_1 = db.Column(db.String(255))
    denomination_usuelle_2 = db.Column(db.String(255))
    denomination_usuelle_3 = db.Column(db.String(255))
    sigle = db.Column(db.String(50))

    # Personne physique
    nom = db.Column(db.String(100))
    nom_usage = db.Column(db.String(100))
    prenom_1 = db.Column(db.String(100))
    prenom_2 = db.Column(db.String(100))
    prenom_3 = db.Column(db.String(100))
    prenom_4 = db.Column(db.String(100))
    prenom_usuel = db.Column(db.String(100))
    pseudonyme = db.Column(db.String(100))
    sexe = db.Column(db.String(1))

    # Caractéristiques
    categorie_juridique = db.Column(db.String(10), index=True)
    activite_principale = db.Column(db.String(10), index=True)
    nomenclature_activite = db.Column(db.String(10))
    categorie_entreprise = db.Column(db.String(5), index=True)
    tranche_effectifs = db.Column(db.String(5), index=True)
    annee_effectifs = db.Column(db.Integer)

    # Statut
    etat_administratif = db.Column(db.String(1), index=True)
    economie_sociale_solidaire = db.Column(db.String(1))
    societe_mission = db.Column(db.String(1))
    caractere_employeur = db.Column(db.String(1))

    # Dates
    date_creation = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    date_dernier_traitement = db.Column(db.DateTime)

    # Siège
    nic_siege = db.Column(db.String(5))

    # Autres
    identifiant_association = db.Column(db.String(20))
    statut_diffusion = db.Column(db.String(1))
    nombre_periodes = db.Column(db.Integer)
    unite_purgee = db.Column(db.String(1))
    annee_categorie_entreprise = db.Column(db.Integer)

    # Relations
    etablissements = db.relationship('Etablissement', backref='unite_legale', lazy='dynamic')

    @property
    def nom_complet(self):
        """Retourne le nom complet (dénomination ou nom/prénom)"""
        if self.denomination:
            return self.denomination
        parts = [self.prenom_usuel or self.prenom_1, self.nom]
        return ' '.join(filter(None, parts)) or 'Non renseigné'

    @property
    def est_active(self):
        """Vérifie si l'entreprise est active"""
        return self.etat_administratif == 'A'

    @property
    def siret_siege(self):
        """Retourne le SIRET du siège"""
        if self.nic_siege:
            return f"{self.siren}{self.nic_siege}"
        return None

    def to_dict(self):
        """Sérialisation pour API"""
        return {
            'siren': self.siren,
            'denomination': self.nom_complet,
            'sigle': self.sigle,
            'categorie_juridique': self.categorie_juridique,
            'activite_principale': self.activite_principale,
            'categorie_entreprise': self.categorie_entreprise,
            'tranche_effectifs': self.tranche_effectifs,
            'etat_administratif': self.etat_administratif,
            'est_active': self.est_active,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'siret_siege': self.siret_siege
        }

    def __repr__(self):
        return f'<UniteLegale {self.siren} - {self.nom_complet}>'
