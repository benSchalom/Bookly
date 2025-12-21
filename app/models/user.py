from datetime import datetime, timezone
from app import db
import bcrypt

class User (db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(255),unique=True, nullable=False, index =True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('client', 'pro', name='user_role'), nullable = False)
    nom = db.Column(db.String(100), nullable =False)
    prenom = db.Column (db.String(100), nullable = False)
    telephone = db.Column(db.String(100), nullable =False)
    photo_url= db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone = True), default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, index=True)
    email_verified = db.Column(db.Boolean, default=False)


    def __init__(self, email, password, role, nom, prenom, telephone):
        #constructeur
        self.email = email
        self.set_password(password)
        self.role = role
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone

    def set_password(self, password):
        # Hasher le mot de passe
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt() #utilisation d'une cle de cryptographie unique par mot de passe
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    def check_password(self, password):
        # Verifier le mot de passe
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def to_dict(self):
        #Convertir en dictionnaire (pour JSON)
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'email_verified': self.email_verified
        }
    
    def __repr__(self): #utiliser pour le debogage
        #Représentation string
        return f'<User {self.email} ({self.role})>'