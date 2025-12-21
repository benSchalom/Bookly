from datetime import datetime, timezone
from app import db

class Pro(db.Model):
    __tablename__ = 'pros'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text)
    specialite_id = db.Column(db.Integer, db.ForeignKey('specialites.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)) 
    
    # Adresse
    adresse_salon = db.Column(db.String(255))
    ville = db.Column(db.String(100), index=True)
    code_postal = db.Column(db.String(10))
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    
    # Modes de travail
    travail_salon = db.Column(db.Boolean, default=True)
    travail_domicile = db.Column(db.Boolean, default=False)
    
    # Frais déplacement (JSON)
    frais_deplacement = db.Column(db.JSON, comment='Paliers frais déplacement, frais en focntion d\'une distance')
    distance_max_km = db.Column(db.Integer, default=20)
    
    # Stats
    rating_avg = db.Column(db.Numeric(3, 2), default=0.00)
    total_reviews = db.Column(db.Integer, default=0)
    total_appointments = db.Column(db.Integer, default=0)
    
    # Sanctions annulations tardives
    late_cancellation_count = db.Column(db.Integer, default=0)
    last_late_cancellation = db.Column(db.DateTime)
    invisible_until = db.Column(db.DateTime, comment='Invisible dans recherche jusqu\'à cette date')

    # Relations
    user = db.relationship('User', backref=db.backref('pro', uselist=False))
    specialite = db.relationship('Specialite', backref='pros')

    def __init__(self, user_id, business_name, specialite_id):
        #constructeur
        self.user_id = user_id
        self.business_name = business_name
        self.specialite_id = specialite_id
    
    def to_dict(self): #aide au json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'business_name': self.business_name,
            'bio': self.bio,
            'specialite_id': self.specialite_id,
            'adresse_salon': self.adresse_salon,
            'ville': self.ville,
            'code_postal': self.code_postal,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'travail_salon': self.travail_salon,
            'travail_domicile': self.travail_domicile,
            'frais_deplacement': self.frais_deplacement,
            'distance_max_km': self.distance_max_km,
            'rating_avg': float(self.rating_avg) if self.rating_avg else 0,
            'total_reviews': self.total_reviews,
            'total_appointments': self.total_appointments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Pro {self.business_name}>'

