from app import create_app, db
from app.models import Specialite

app = create_app('development')

with app.app_context():
    # Vérifier si il y'a deja des donnes dans la bd afin de ne pas corrompre nos données
    if Specialite.query.count() > 0:
        print(" Spécialités déjà présentes dans la DB")
        for spec in Specialite.query.all():
            print(f"   - {spec.nom}")
        exit()
    
    # Créer les 6 spécialités (uniquement dans la cas où on n'a pas encore de spécialité)
    specialites = [ # nom, slug, description 
        Specialite('Coiffeur', 'coiffeur', 'Services de coiffure et coupe de cheveux'),
        Specialite('Esthéticienne', 'estheticienne', 'Soins esthétiques et beauté'),
        Specialite('Barbier', 'barbier', 'Coupe et entretien barbe'),
        Specialite('Maquilleur', 'maquilleur', 'Services de maquillage professionnel'),
        Specialite('Manucure', 'manucure', 'Soins des ongles et manucure'),
        Specialite('Autre', 'autre', 'Autres services beauté et bien-être'),
        Specialite('Salon Mixte', 'salon-mixte', 'Services multiples : coiffure, esthétique, manucure'),
    ]
    
    # Gestion de l'ordre d'affichage
    for i, spec in enumerate(specialites, start=1):
        spec.ordre_affichage = i if spec.slug != 'autre' else 99 #on s'assure que la spécialité "autre" si existante soit affiché en derniere
        db.session.add(spec)
    
    # Commit
    db.session.commit()
    
    print("6 spécialités insérées avec succès:")
    for spec in Specialite.query.order_by(Specialite.ordre_affichage).all():
        print(f"   {spec.ordre_affichage}. {spec.nom} ({spec.slug})")