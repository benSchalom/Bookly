from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.service import Service
from app.models.specialite import Specialite

def test_user_creation(app):
    """Test user creation and password hashing."""
    with app.app_context():
        user = User(
            email='test@example.com',
            password='password123',
            role='client',
            nom='Doe',
            prenom='John',
            telephone='1234567890'
        )
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.check_password('password123')
        assert not user.check_password('wrongpass')
        assert user.role == 'client'

def test_pro_creation(app):
    """Test pro creation with relations."""
    with app.app_context():
        # Create User for Pro
        user = User(
            email='pro@example.com',
            password='password123',
            role='pro',
            nom='Pro',
            prenom='Master',
            telephone='0987654321'
        )
        db.session.add(user)
        db.session.commit() # Commit to get ID

        # Create Specialite
        specialite = Specialite(
            nom='Coiffure',
            slug='coiffure',
            description='Coupe et coiffure'
        )
        db.session.add(specialite)
        db.session.commit()

        # Create Pro
        pro = Pro(
            user_id=user.id,
            business_name='Best Cuts',
            specialite_id=specialite.id,
            adresse_salon='123 Main St',
            ville='Montreal',
            pays='Canada',
            province='Quebec'
        )
        db.session.add(pro)
        db.session.commit()

        assert pro.id is not None
        assert pro.user.email == 'pro@example.com'
        assert pro.specialite.nom == 'Coiffure'
        assert pro.business_name == 'Best Cuts'

def test_service_creation(app):
    """Test service creation."""
    with app.app_context():
        # Setup Pro (reuse code or fixture would be better but this is explicit)
        user = User(email='service_pro@example.com', password='pw', role='pro', nom='S', prenom='P', telephone='000')
        db.session.add(user)
        db.session.flush()
        
        spec = Specialite(nom='TestSpec', slug='testspec')
        db.session.add(spec)
        db.session.flush()
        
        pro = Pro(user_id=user.id, business_name='Service Biz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.commit()

        # Create Service
        service = Service(
            pro_id=pro.id,
            nom='Coupe Homme',
            duree_minutes=30,
            prix=35.00,
            disponible_salon=True
        )
        db.session.add(service)
        db.session.commit()

        assert service.id is not None
        assert service.pro.business_name == 'Service Biz'
        assert service.prix == 35.00
