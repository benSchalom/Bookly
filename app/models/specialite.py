from datetime import datetime, timezone
from app import db

class Specialite(db.Model):
    __tablename__ = 'specialites'

    id = db.Column(db.Integer, primary_key= True)
    nom = db.Column(db.String(100), unique=True, nullable = False)
    slug = db.Column(db.String(100), unique = True, nullable = False, index= True)
    description = db.Column(db.Text)
    icone_url = db.Column (db. String(255))
    is_active = db.Column(db.Boolean, default= True, index = True)
    ordre_affichage = db.Column(db.Integer, default = 0)
    created_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc))

    def __init__(self, nom, slug, description=None):
        #constructeur
        self.nom = nom
        self.slug = slug
        self.description= description

    def to_dict(self): #aide au json
        return {
            'id': self.id,
            'nom': self.nom,
            'slug': self.slug,
            'description': self.description,
            'icone_url': self.icone_url,
            'is_active': self.is_active,
            'ordre_affichage': self.ordre_affichage
        }  

    def __repr__(self):
        return f'<Specialite {self.nom}>'     
