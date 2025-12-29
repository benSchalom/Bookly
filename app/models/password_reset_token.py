from app import db
from datetime import datetime, timezone
import secrets

class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id =db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index = True, nullable = False)
    token = db.Column(db.String(255), unique = True, nullable = False, index = True)
    expires_at = db.Column(db.DateTime(timezone = True), nullable = False)
    used = db.Column(db.Boolean, default = False)
    created_at = db.Column(db.DateTime(timezone = True), default = lambda:datetime.now(timezone.utc))

    user =db.relationship('User', backref = 'pass_reset')

    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32) 
    
    def is_valid(self):
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return not self.used and expires > now
    
    def __repr__(self):
        return f'<PasswordResetToken User:{self.user_id} Valid:{self.is_valid()}>'