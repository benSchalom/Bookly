from app import db
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint

class Review (db.Model):
    __tablename__ = 'reviews'

    __table_args__ = (
        CheckConstraint ('rating >=1 AND rating <=5', name ='check_rating_range'),
    )

    id = db.Column(db.Integer, primary_key =True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False, index = True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index = True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable = True, unique = True, index = True)
    rating = db.Column(db.Integer, nullable = False)
    commentaire = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc))

    client = db.relationship('User', foreign_keys =[client_id], backref ='reviews_as_client') # Les avis que le client a ecrit
    pro = db.relationship('Pro', backref = 'reviews') # avis laisser par les clients sur les rdv du pro
    appointment =db.relationship('Appointment', backref ='review') # avis laisser par le client sur un rdv specifique

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'client_nom': f"{self.client.prenom} {self.client.nom}" if self.client else None,
            'pro_id': self.pro_id,
            'appointment_id': self.appointment_id,
            'rating': self.rating,
            'commentaire': self.commentaire,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Avis: client: {self.client_id}, rendez-vous: {self.appointment_id}, commentaire: {self.commentaire}>'