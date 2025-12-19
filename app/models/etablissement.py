from app import db


class Etablissement(db.Model):
    """Modèle pour les établissements"""
    __tablename__ = 'etablissement'

    siret = db.Column(db.String(14), primary_key=True)
    siren = db.Column(db.String(9), db.ForeignKey('unite_legale.siren'), nullable=False, index=True)
    nic = db.Column(db.String(5), nullable=False)

    # Caractéristiques
    etablissement_siege = db.Column(db.Boolean, index=True)
    etat_administratif = db.Column(db.String(1), index=True)
    activite_principale = db.Column(db.String(10), index=True)
    nomenclature_activite = db.Column(db.String(10))
    activite_registre_metiers = db.Column(db.String(10))
    tranche_effectifs = db.Column(db.String(5))
    annee_effectifs = db.Column(db.Integer)
    caractere_employeur = db.Column(db.String(1))

    # Dénomination
    denomination_usuelle = db.Column(db.String(255))
    enseigne_1 = db.Column(db.String(255))
    enseigne_2 = db.Column(db.String(255))
    enseigne_3 = db.Column(db.String(255))

    # Adresse principale
    numero_voie = db.Column(db.String(10))
    indice_repetition = db.Column(db.String(5))
    dernier_numero_voie = db.Column(db.String(10))
    indice_repetition_dernier = db.Column(db.String(5))
    type_voie = db.Column(db.String(10))
    libelle_voie = db.Column(db.String(255))
    complement_adresse = db.Column(db.String(255))
    distribution_speciale = db.Column(db.String(100))
    code_postal = db.Column(db.String(10), index=True)
    libelle_commune = db.Column(db.String(100), index=True)
    code_commune = db.Column(db.String(10), index=True)
    code_cedex = db.Column(db.String(10))
    libelle_cedex = db.Column(db.String(100))

    # Adresse à l'étranger
    code_pays_etranger = db.Column(db.String(10))
    libelle_pays_etranger = db.Column(db.String(100))
    libelle_commune_etranger = db.Column(db.String(100))

    # Géolocalisation
    coordonnee_lambert_x = db.Column(db.Numeric(15, 2))
    coordonnee_lambert_y = db.Column(db.Numeric(15, 2))
    identifiant_adresse = db.Column(db.String(50))

    # Dates
    date_creation = db.Column(db.Date)
    date_debut = db.Column(db.Date)
    date_dernier_traitement = db.Column(db.DateTime)

    # Autres
    statut_diffusion = db.Column(db.String(1))
    nombre_periodes = db.Column(db.Integer)

    @property
    def adresse_complete(self):
        """Retourne l'adresse formatée"""
        parts = [
            self.numero_voie,
            self.indice_repetition,
            self.type_voie,
            self.libelle_voie
        ]
        ligne1 = ' '.join(filter(None, parts))

        if self.complement_adresse:
            ligne1 = f"{ligne1}, {self.complement_adresse}"

        ligne2 = f"{self.code_postal or ''} {self.libelle_commune or ''}".strip()

        return f"{ligne1}\n{ligne2}".strip()

    @property
    def adresse_ligne(self):
        """Retourne l'adresse sur une seule ligne"""
        return self.adresse_complete.replace('\n', ', ')

    @property
    def est_actif(self):
        """Vérifie si l'établissement est actif"""
        return self.etat_administratif == 'A'

    @property
    def nom_affiche(self):
        """Retourne le nom à afficher"""
        return self.denomination_usuelle or self.enseigne_1 or f"Établissement {self.nic}"

    def to_dict(self):
        """Sérialisation pour API"""
        return {
            'siret': self.siret,
            'siren': self.siren,
            'nic': self.nic,
            'denomination': self.nom_affiche,
            'enseigne': self.enseigne_1,
            'est_siege': self.etablissement_siege,
            'etat_administratif': self.etat_administratif,
            'est_actif': self.est_actif,
            'activite_principale': self.activite_principale,
            'adresse': self.adresse_ligne,
            'code_postal': self.code_postal,
            'ville': self.libelle_commune,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None
        }

    def __repr__(self):
        return f'<Etablissement {self.siret} - {self.nom_affiche}>'
