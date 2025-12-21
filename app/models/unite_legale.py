from app import db


class UniteLegale(db.Model):
    """Modèle pour les unités légales (entreprises)"""
    __tablename__ = 'unite_legale'

    siren = db.Column(db.Text, primary_key=True)

    # Identification
    denomination = db.Column(db.Text, index=True)
    denomination_usuelle_1 = db.Column(db.Text)
    denomination_usuelle_2 = db.Column(db.Text)
    denomination_usuelle_3 = db.Column(db.Text)
    sigle = db.Column(db.Text)

    # Personne physique
    nom = db.Column(db.Text)
    nom_usage = db.Column(db.Text)
    prenom_1 = db.Column(db.Text)
    prenom_2 = db.Column(db.Text)
    prenom_3 = db.Column(db.Text)
    prenom_4 = db.Column(db.Text)
    prenom_usuel = db.Column(db.Text)
    pseudonyme = db.Column(db.Text)
    sexe = db.Column(db.Text)

    # Caractéristiques
    categorie_juridique = db.Column(db.Text, index=True)
    activite_principale = db.Column(db.Text, index=True)
    nomenclature_activite = db.Column(db.Text)
    categorie_entreprise = db.Column(db.Text, index=True)
    tranche_effectifs = db.Column(db.Text, index=True)
    annee_effectifs = db.Column(db.Text)

    # Statut
    etat_administratif = db.Column(db.Text, index=True)
    economie_sociale_solidaire = db.Column(db.Text)
    societe_mission = db.Column(db.Text)
    caractere_employeur = db.Column(db.Text)

    # Dates (stockées comme TEXT)
    date_creation = db.Column(db.Text)
    date_debut = db.Column(db.Text)
    date_dernier_traitement = db.Column(db.Text)

    # Siège
    nic_siege = db.Column(db.Text)

    # Autres
    identifiant_association = db.Column(db.Text)
    statut_diffusion = db.Column(db.Text)
    nombre_periodes = db.Column(db.Text)
    unite_purgee = db.Column(db.Text)
    annee_categorie_entreprise = db.Column(db.Text)

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
            'date_creation': self.date_creation,
            'siret_siege': self.siret_siege
        }

    def __repr__(self):
        return f'<UniteLegale {self.siren} - {self.nom_complet}>'
