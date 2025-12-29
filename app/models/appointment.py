from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint


#Declaration de la classe 
class Appointment(db.Model):
    __tablename__ = 'appointments'

    __table_args__ = (
        CheckConstraint('heure_debut < heure_fin', name='check_heures_coherences_appointment'),
    )

    id = db.Column(db.Integer, primary_key = True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index = True) 
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, index = True) 
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable = False, index = True)

    # Informations du rendez vous
    date = db.Column(db.Date, nullable = False, index = True)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    type_rdv = db.Column(db.Enum('Salon', 'Domicile', name='type_rdv_enum'), nullable = False)
    statut = db.Column(db.Enum('En attente', 'Confirmer', 'Terminer', 'Annuler', name='statut_enum'), default = 'En attente', nullable = False)
    notes_client = db.Column(db.Text, nullable=True)
    notes_pro = db.Column(db.Text, nullable=True)
    adresse_domicile = db.Column(db.String(255), nullable=True)
    distance_km = db.Column(db.Numeric(10, 2), nullable=True)
    prix_total = db.Column(db.Numeric(10, 2), nullable=False)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancelled_at = db.Column(db.DateTime(timezone=True), nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    is_late_cancellation = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    client = db.relationship('User', foreign_keys=[client_id], backref='appointments_as_client')    
    pro = db.relationship('Pro', backref='appointments')
    service = db.relationship('Service', backref = 'appointments')
    cancelled_by_user = db.relationship('User', foreign_keys=[cancelled_by])


    def to_dict(self):
        # Conversion en json
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_nom': f"{self.client.prenom} {self.client.nom}" if self.client else None,
            'pro_id': self.pro_id,
            'pro_business_name': self.pro.business_name if self.pro else None,
            'service_id': self.service_id,
            'service_nom': self.service.nom if self.service else None,
            'date': self.date.isoformat() if self.date else None,
            'heure_debut': self.heure_debut.strftime('%H:%M') if self.heure_debut else None,
            'heure_fin': self.heure_fin.strftime('%H:%M') if self.heure_fin else None,
            'type_rdv': self.type_rdv,
            'statut': self.statut,
            'prix_total': float(self.prix_total) if self.prix_total else None,
            'adresse_domicile': self.adresse_domicile,
            'distance_km': float(self.distance_km) if self.distance_km else None,
            'cancelled_by': self.cancelled_by,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancellation_reason': self.cancellation_reason,
            'is_late_cancellation': self.is_late_cancellation,
            'notes_client': self.notes_client,
            'notes_client': self.notes_client,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    

    # Affichage ppour les developpeurs
    def __repr__(self):
        return f'<Appointment {self.date} {self.heure_debut} - {self.client.prenom if self.client else "?"} chez {self.pro.business_name if self.pro else "?"}>'