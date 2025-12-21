from app import db


class Etablissement(db.Model):
    """Modèle pour les établissements"""
    __tablename__ = 'etablissement'

    siret = db.Column(db.Text, primary_key=True)
    siren = db.Column(db.Text, db.ForeignKey('unite_legale.siren'), nullable=False, index=True)
    nic = db.Column(db.Text, nullable=False)

    # Caractéristiques
    etablissement_siege = db.Column(db.Text, index=True)
    etat_administratif = db.Column(db.Text, index=True)
    activite_principale = db.Column(db.Text, index=True)
    nomenclature_activite = db.Column(db.Text)
    activite_registre_metiers = db.Column(db.Text)
    tranche_effectifs = db.Column(db.Text)
    annee_effectifs = db.Column(db.Text)
    caractere_employeur = db.Column(db.Text)

    # Dénomination
    denomination_usuelle = db.Column(db.Text)
    enseigne_1 = db.Column(db.Text)
    enseigne_2 = db.Column(db.Text)
    enseigne_3 = db.Column(db.Text)

    # Adresse principale
    numero_voie = db.Column(db.Text)
    indice_repetition = db.Column(db.Text)
    dernier_numero_voie = db.Column(db.Text)
    indice_repetition_dernier = db.Column(db.Text)
    type_voie = db.Column(db.Text)
    libelle_voie = db.Column(db.Text)
    complement_adresse = db.Column(db.Text)
    distribution_speciale = db.Column(db.Text)
    code_postal = db.Column(db.Text, index=True)
    libelle_commune = db.Column(db.Text, index=True)
    code_commune = db.Column(db.Text, index=True)
    code_cedex = db.Column(db.Text)
    libelle_cedex = db.Column(db.Text)

    # Adresse à l'étranger
    code_pays_etranger = db.Column(db.Text)
    libelle_pays_etranger = db.Column(db.Text)
    libelle_commune_etranger = db.Column(db.Text)

    # Adresse secondaire
    numero_voie_2 = db.Column(db.Text)
    indice_repetition_2 = db.Column(db.Text)
    type_voie_2 = db.Column(db.Text)
    libelle_voie_2 = db.Column(db.Text)
    complement_adresse_2 = db.Column(db.Text)
    distribution_speciale_2 = db.Column(db.Text)
    code_postal_2 = db.Column(db.Text)
    libelle_commune_2 = db.Column(db.Text)
    code_commune_2 = db.Column(db.Text)
    code_cedex_2 = db.Column(db.Text)
    libelle_cedex_2 = db.Column(db.Text)
    code_pays_etranger_2 = db.Column(db.Text)
    libelle_pays_etranger_2 = db.Column(db.Text)
    libelle_commune_etranger_2 = db.Column(db.Text)

    # Géolocalisation
    coordonnee_lambert_x = db.Column(db.Text)
    coordonnee_lambert_y = db.Column(db.Text)
    identifiant_adresse = db.Column(db.Text)

    # Dates
    date_creation = db.Column(db.Text)
    date_debut = db.Column(db.Text)
    date_dernier_traitement = db.Column(db.Text)

    # Autres
    statut_diffusion = db.Column(db.Text)
    nombre_periodes = db.Column(db.Text)

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
    def est_siege(self):
        """Vérifie si c'est le siège (gère TEXT 'true'/'false')"""
        return self.etablissement_siege in ('true', 'True', '1', True)

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
            'est_siege': self.est_siege,
            'etat_administratif': self.etat_administratif,
            'est_actif': self.est_actif,
            'activite_principale': self.activite_principale,
            'adresse': self.adresse_ligne,
            'code_postal': self.code_postal,
            'ville': self.libelle_commune,
            'date_creation': self.date_creation
        }

    def __repr__(self):
        return f'<Etablissement {self.siret} - {self.nom_affiche}>'
