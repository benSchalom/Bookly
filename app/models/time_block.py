from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint


class TimeBlock(db.Model):
    __tablename__ = 'time_blocks'

    __table_args__ = (
        CheckConstraint('date_debut < date_fin', name='check_date_coherentes'),
    )

    id = db.Column(db.Integer, primary_key=True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable=False, index=True)
    date_debut = db.Column(db.DateTime(timezone=True), nullable = False)
    date_fin = db.Column(db.DateTime(timezone=True), nullable = False)
    raison = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    pro = db.relationship('Pro', backref='time_blocks')

    def to_dict(self):
        #Convertir en dictionnaire (pour JSON)
        return {
            'id': self.id,
            'pro_id': self.pro_id,
            'date_debut': self.date_debut.isoformat() if self.date_debut else None,
            'date_fin': self.date_fin.isoformat() if self.date_fin else None,
            'raison': self.raison,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TimeBlock {self.date_debut.date()} au {self.date_fin.date()} - {self.raison}>'
