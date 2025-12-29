from app import db
from datetime import datetime, timezone
from sqlalchemy import UniqueConstraint

class LoyaltyAccount(db.Model):
    __tablename__ = 'loyalty_accounts'

    __table_args__ = (
        UniqueConstraint('client_id', 'pro_id', name='unique_client_pro'),
    )

    id = db.Column(db.Integer, primary_key = True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True, nullable = False)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index =True)
    points_total = db.Column(db.Integer, default =0 )
    late_cancellation_count = db.Column(db.Integer, default =0)
    last_late_cancellation = db.Column(db.DateTime(timezone = True))
    created_at = db.Column(db.DateTime(timezone = True), default =lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    client = db.relationship('User', foreign_keys = [client_id], backref ='loyalty_account_as_client')
    pro = db.relationship('Pro', backref = 'loyality_account_as_pro')

    # Conversion en dictionnaire
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'pro_id': self.pro_id,
            'business_name': self.pro.business_name if self.pro else None,
            'points_total': self.points_total,
            'late_cancellation_count': self.late_cancellation_count,
            'last_late_cancellation': self.last_late_cancellation.isoformat() if self.last_late_cancellation else None,
            'alerte_annulations': self.late_cancellation_count >= 3,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    # Methode d'affichage pour moi dans la console en test
    def __repr__(self):
        return f'<Loyality Account: Pro: {self.pro_id}, client: {self.client_id}, Points: {self.points_total}>'