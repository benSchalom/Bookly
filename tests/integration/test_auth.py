from app import db
from app.models.specialite import Specialite

def test_client_signup(client):
    """Test inscription client."""
    response = client.post('/api/auth/inscription', json={
        'email': 'client@test.com',
        'password': 'Password123!',
        'nom': 'Client',
        'prenom': 'Test',
        'telephone': '1234567890'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['email'] == 'client@test.com'

def test_pro_signup(client, app):
    """Test inscription professionnel."""
    # Seed specialite required for pro signup
    with app.app_context():
        spec = Specialite(nom='Coiffure', slug='coiffure', description='Desc')
        db.session.add(spec)
        db.session.commit()
        spec_id = spec.id

    response = client.post('/api/auth/inscription-pro', json={
        'email': 'pro@test.com',
        'password': 'Password123!',
        'nom': 'Pro',
        'prenom': 'Test',
        'telephone': '0987654321',
        'business_name': 'Test Biz',
        'specialite_id': spec_id,
        'ville': 'Montreal',
        'adresse_salon': '123 St',
        'pays': 'Canada',
        'province': 'Quebec'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert 'pro' in data
    assert 'user' in data
    assert data['pro']['business_name'] == 'Test Biz'

def test_login(client):
    """Test connexion."""
    # Create user first
    client.post('/api/auth/inscription', json={
        'email': 'login@test.com',
        'password': 'Password123!',
        'nom': 'Nom',
        'prenom': 'Prenom',
        'telephone': '1112223333'
    })

    # Test login success
    response = client.post('/api/auth/connexion', json={
        'email': 'login@test.com',
        'password': 'Password123!'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['message'] == 'Connexion réussie.'

    # Test login failure
    response_fail = client.post('/api/auth/connexion', json={
        'email': 'login@test.com',
        'password': 'WrongPassword'
    })
    assert response_fail.status_code == 401

def test_protected_route_moi(client):
    """Test protected route access."""
    # Register and login to get token
    client.post('/api/auth/inscription', json={
        'email': 'moi@test.com',
        'password': 'Password123!',
        'nom': 'Moi',
        'prenom': 'Moi',
        'telephone': '5555555555'
    })
    login_resp = client.post('/api/auth/connexion', json={
        'email': 'moi@test.com',
        'password': 'Password123!'
    })
    token = login_resp.get_json()['access_token']

    # Access protected route
    response = client.get('/api/auth/moi', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.get_json()['user']['email'] == 'moi@test.com'

    # Access without token
    response_no_token = client.get('/api/auth/moi')
    assert response_no_token.status_code == 401
