from app import create_app, db
from app.models.service import Service
from app.models.pro import Pro
from app.models.user import User

# Créer l'app
app = create_app()

with app.app_context():
    # Trouver un pro existant (Sophie créée hier)
    user_pro = User.query.filter_by(email='sophie@coiffure.com').first()
    
    if user_pro and user_pro.pro:
        pro = user_pro.pro
        
        # Créer un service de test
        service = Service(
            pro_id=pro.id,
            nom='Coupe homme',
            description='Coupe aux ciseaux avec shampoing',
            duree_minutes=30,
            prix=25.00,
            disponible_salon=True,
            disponible_domicile=True,
            ordre_affichage=1
        )
        
        # Ajouter à la DB
        db.session.add(service)
        db.session.commit()
        
        print(" Service créé avec succès !")
        print(service)  # Teste __repr__()
        print("\nDictionnaire JSON :")
        print(service.to_dict())  # Teste to_dict()
        
        # Tester la relation
        print(f" Pro : {service.pro.business_name}")
        print(f" Services du pro : {len(pro.services)}")
        
    else:
        print("Pro Sophie non trouvé. Crée-le d'abord !")