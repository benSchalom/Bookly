from app import db
from datetime import datetime, timezone

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key = True)
    pro_id = db.Column(db.Integer, db.ForeignKey('pros.id'), nullable = False, index = True) 
    image_url = db.Column(db.String(255), nullable = False)
    description = db.Column(db.Text)
    ordre_affichage = db.Column(db.Integer, default = 0)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    pro = db.relationship('Pro', backref='portfolios')


    def to_dict(self):
        # Conversion en json
        return {
            'id': self.id,
            'pro_id': self.pro_id,
            'image_url': self.image_url,
            'description': self.description,
            'ordre_affichage': self.ordre_affichage,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    

    def __repr__(self):
        return f'<Portfolio Pro:{self.pro_id} Image:{self.id}>' 
     