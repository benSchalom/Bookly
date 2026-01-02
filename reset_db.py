import os
from app import create_app, db

# Importation de tous les modeles
from app.models import *

def reset_database():
    
    # Vérifier qu'on n'est pas en production
    if os.getenv('FLASK_ENV') == 'production':
        print("ERREUR: Impossible de réinitialiser la DB en production!")
        return
    
    app = create_app('development')
    
    with app.app_context():
        print("\nSuppression de toutes les tables...")
        db.drop_all()
        print("Tables supprimées")
        
        print("\nCréation des nouvelles tables...")
        db.create_all()
        print("Tables créées")
        
        print("\nInsertion des spécialités...")
        
        # Créer les spécialités 
        specialites = [
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
            spec.ordre_affichage = i if spec.slug != 'autre' else 99
            db.session.add(spec)
        
        # Commit
        db.session.commit()
        
        print(f"{len(specialites)} spécialités insérées:")
        for spec in Specialite.query.order_by(Specialite.ordre_affichage).all():
            print(f"   {spec.ordre_affichage}. {spec.nom} ({spec.slug})")
        
        # Afficher résumé de toutes les tables
        print("\n" + "="*60)
        print("Base de données réinitialisée avec succès!")
        print("="*60)
        print("\nÉtat de la base de données:")
        print(f"   Users: {User.query.count()}")
        print(f"   Pros: {Pro.query.count()}")
        print(f"   Spécialités: {Specialite.query.count()}")
        print(f"   Services: {Service.query.count()}")
        print(f"   Availabilities: {Availability.query.count()}")
        print(f"   TimeBlocks: {TimeBlock.query.count()}")
        print(f"   Appointments: {Appointment.query.count()}")
        print(f"   Portfolios: {Portfolio.query.count()}")
        print(f"   LoyaltyAccounts: {LoyaltyAccount.query.count()}")
        print(f"   LoyaltyHistory: {LoyaltyHistory.query.count()}")
        print(f"   Reviews: {Review.query.count()}")
        print(f"   PasswordResetTokens: {PasswordResetToken.query.count()}")

if __name__ == '__main__':
    reset_database()