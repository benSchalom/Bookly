from app import create_app, db
from app.models import User, Pro, Specialite

app = create_app('development')

with app.app_context():
    print("TEST: Création User + Pro")
    print("-" * 50)
    
    # 1. Récupérer une spécialité
    coiffeur = Specialite.query.filter_by(slug='coiffeur').first()
    print(f"Spécialité trouvée: {coiffeur.nom}")
    
    # 2. Créer un User PRO
    user_pro = User(
        email='salon.ben@bookly.app',
        password='SecurePass123!',
        role='pro',
        nom='Coiffure',
        prenom='Ben',
        telephone='+15141234567'
    )
    db.session.add(user_pro)
    db.session.commit()
    print(f"User créé: {user_pro.email} (ID: {user_pro.id})")
    
    # 3. Créer le profil Pro
    pro = Pro(
        user_id=user_pro.id,
        business_name='Salon de Ben',
        specialite_id=coiffeur.id
    )
    pro.bio = 'Le meilleur salon de Montréal !'
    pro.adresse_salon = '123 Rue Saint-Denis'
    pro.ville = 'Montréal'
    pro.code_postal = 'H2X 1K1'
    pro.travail_salon = True
    pro.travail_domicile = True
    pro.frais_deplacement = [
        {"max_km": 5, "prix": 10},
        {"max_km": 10, "prix": 20},
        {"max_km": 15, "prix": 30}
    ]
    
    db.session.add(pro)
    db.session.commit()
    print(f"Pro créé: {pro.business_name} (ID: {pro.id})")
    
    print("-" * 50)
    print("RELATIONS:")
    
    # Test relations
    print(f"   User → Pro: {user_pro.pro.business_name}")
    print(f"   Pro → User: {pro.user.email}")
    print(f"   Pro → Specialite: {pro.specialite.nom}")
    
    print("-" * 50)
    print("TO_DICT:")
    print(f"   User: {user_pro.to_dict()}")
    print(f"   Pro: {pro.to_dict()}")
    
    print("-" * 50)
    print("TEST RÉUSSI !")