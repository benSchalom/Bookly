from app import db
from datetime import datetime, timezone

class LoyaltyHistory(db.Model):
    __tablename__ = 'loyalty_histories'

    id = db.Column(db.Integer, primary_key = True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True, nullable = False)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index =True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), index= True)
    points_change = db.Column(db.Integer, default = 0)
    raison = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone = True), default = lambda:datetime.now(timezone.utc))

    client =db.relationship('User', backref = 'loyalty_history_as_client')
    pro = db.relationship('Pro', backref = 'loyalty_history_as_pro')
    appointment = db.relationship('Appointment', backref = 'loyality_history')

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'appointment_id': self.appointment_id,
            'points_change': self.points_change,
            'raison': self.raison,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
