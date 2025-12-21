from app import create_app, db
from app.models.user import User

# Créer l'app
app = create_app('development')

with app.app_context():
    # Créer les tables si elles n'existent pas
    db.create_all()
    
    # Créer un utilisateur de test
    user = User(
        email='test@bookly.app',
        password='password123',
        role='client',
        nom='Test',
        prenom='User',
        telephone='+15141234567'
    )   
    
    # Ajouter à la DB
    db.session.add(user)
    db.session.commit()
    
    print(f" User créé: {user}")
    print(f" Email: {user.email}")
    print(f" Password hash: {user.password_hash[:50]}...")
    print(f" Password check: {user.check_password('password123')}")
    print(f" Wrong password: {user.check_password('wrongpass')}")
    print(f"Dict: {user.to_dict()}")
