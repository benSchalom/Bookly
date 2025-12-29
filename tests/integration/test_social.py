import pytest
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite
from app.models.review import Review
from app.models.portfolio import Portfolio

@pytest.fixture
def social_setup(client, app):
    """Setup for social tests."""
    with app.app_context():
        # Create Pro
        spec = Specialite(nom='SocialSpec', slug='socialspec')
        db.session.add(spec)
        pro_user = User(email='socialpro@test.com', password='pw', role='pro', nom='P', prenom='P', telephone='1112223333')
        db.session.add(pro_user)
        db.session.flush()
        pro = Pro(user_id=pro_user.id, business_name='SocialBiz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.commit()
        
        pro_id = pro.id
        
        # Create Client
        client_user = User(email='socialclient@test.com', password='pw', role='client', nom='C', prenom='C', telephone='4445556666')
        db.session.add(client_user)
        db.session.commit()
        
    # Login Pro
    resp = client.post('/api/auth/connexion', json={'email': 'socialpro@test.com', 'password': 'pw'})
    pro_token = resp.get_json()['access_token']
    
    # Login Client
    resp = client.post('/api/auth/connexion', json={'email': 'socialclient@test.com', 'password': 'pw'})
    client_token = resp.get_json()['access_token']
    
    return {
        'pro_id': pro_id,
        'pro_token': pro_token,
        'client_token': client_token
    }

def test_reviews_lifecycle(client, social_setup):
    """Test Create, List reviews."""
    pro_id = social_setup['pro_id']
    client_token = social_setup['client_token']
    headers = {'Authorization': f'Bearer {client_token}'}
    
    # 1. Create Review
    resp = client.post('/api/reviews', json={
        'pro_id': pro_id,
        'rating': 5,
        'commentaire': 'Great service!'
    }, headers=headers)
    assert resp.status_code == 201
    
    # 2. Prevent Duplicate Review
    resp = client.post('/api/reviews', json={
        'pro_id': pro_id,
        'rating': 4,
        'commentaire': 'Again?'
    }, headers=headers)
    assert resp.status_code == 400
    assert 'Vous avez déjà soumis une évaluation pour ce professionnel.' in resp.get_json()['error']
    
    # 3. List Reviews for Pro
    resp = client.get(f'/api/pros/{pro_id}/reviews') # Public endpoint usually
    assert resp.status_code == 200
    reviews = resp.get_json()['reviews'] # Check key name
    assert len(reviews) == 1
    assert reviews[0]['rating'] == 5

def test_portfolio_management(client, social_setup):
    """Test Portfolio add/delete (Pro only)."""
    pro_token = social_setup['pro_token']
    headers = {'Authorization': f'Bearer {pro_token}'}
    
    # 1. Add Image
    # Note: If endpoint accepts URL
    resp = client.post('/api/pros/portfolios', json={
        'image_url': 'http://test.com/img.jpg',
        'description': 'My Work'
    }, headers=headers)
    assert resp.status_code == 201
    portfolio = resp.get_json()['Portfolio']
    portfolio_id = portfolio['id']
    
    # 2. List Portfolio
    # Delete
    resp = client.delete(f'/api/pros/portfolios/{portfolio_id}', headers=headers)
    assert resp.status_code == 200
