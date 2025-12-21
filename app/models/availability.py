from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint

class Availability(db.Model):
    __tablename__ = 'availabilities'
    
    __table_args__ = (
        CheckConstraint('heure_debut < heure_fin', name='check_heures_coherences'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable=False, index=True)
    jour_semaine = db.Column(db.Integer, CheckConstraint('jour_semaine >= 0 AND jour_semaine < 7'), nullable=False, index=True)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    pro = db.relationship('Pro', backref='availabilities')
    
    def to_dict(self):
        #Convertir en dictionnaire (pour JSON)
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return {
            'id': self.id,
            'pro_id': self.pro_id,
            'jour_semaine': self.jour_semaine,
            'jour_nom': jours[self.jour_semaine],
            'heure_debut': self.heure_debut.strftime('%H:%M') if self.heure_debut else None,
            'heure_fin': self.heure_fin.strftime('%H:%M') if self.heure_fin else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        return f'<Availability {jours[self.jour_semaine]} {self.heure_debut}-{self.heure_fin}>'