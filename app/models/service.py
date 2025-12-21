from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint


#Declaration de la classe 
class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key = True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index = True) 

    # Informations du service
    nom = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duree_minutes = db.Column(db.Integer,CheckConstraint('duree_minutes > 0'), nullable=False)
    prix = db.Column(db.Numeric(10, 2),CheckConstraint('prix >= 0'), nullable=False)
    disponible_salon = db.Column(db.Boolean, default=True)
    disponible_domicile = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    ordre_affichage = db.Column(db.Integer, default=0)
    points_fidelite = db.Column(db.Integer, default=10) #Nombre de points obtenu apres chaque execution de ce service
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    #relation a la table pro (un  pro a plusieur service, un service appartient a un pro)
    pro = db.relationship('Pro', backref='services')

    def to_dict(self):
        # Transformer les informations d'un service en dictionnaire
        return {
            'id': self.id,
            'pro_id': self.pro_id,
            'nom': self.nom,
            'description': self.description,
            'duree_minutes': self.duree_minutes,
            'prix': float(self.prix),
            'disponible_salon': self.disponible_salon,
            'disponible_domicile': self.disponible_domicile,
            'is_active': self.is_active,
            'ordre_affichage': self.ordre_affichage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    

    def __repr__(self):
        # Représentation string pour debugging
        
        return f'<Service {self.nom} - {self.duree_minutes}min - {self.prix}$>'