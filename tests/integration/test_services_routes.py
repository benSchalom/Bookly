import pytest
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite

@pytest.fixture
def pro_auth_headers(client, app):
    """Setup pro, login and return headers."""
    with app.app_context():
        # Specialite
        spec = Specialite(nom='Coiffure', slug='coiffure')
        db.session.add(spec)
        db.session.flush()

        # Pro User
        user = User(email='pro@services.com', password='pw', role='pro', nom='P', prenom='P', telephone='000')
        db.session.add(user)
        db.session.flush()

        # Pro Profile
        pro = Pro(user_id=user.id, business_name='ServiceBiz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.commit()

    # Login
    login_resp = client.post('/api/auth/connexion', json={'email': 'pro@services.com', 'password': 'pw'})
    token = login_resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_service_crud_lifecycle(client, pro_auth_headers):
    """Test Create, Read, Update, Delete for Service."""
    
    # 1. Create Service
    create_resp = client.post('/api/pros/services', json={
        'nom': 'New Cut',
        'duree_minutes': 30,
        'prix': 25.0
    }, headers=pro_auth_headers)
    
    assert create_resp.status_code == 201
    service_id = create_resp.get_json()['service']['id']
    assert create_resp.get_json()['service']['nom'] == 'New Cut'

    # 2. List Services
    list_resp = client.get('/api/pros/services', headers=pro_auth_headers)
    assert list_resp.status_code == 200
    services = list_resp.get_json()['services']
    assert len(services) >= 1
    assert services[0]['nom'] == 'New Cut'

    # 3. Update Service
    max_price = 30.0
    update_resp = client.put(f'/api/pros/services/{service_id}', json={
        'prix': max_price
    }, headers=pro_auth_headers)
    
    assert update_resp.status_code == 200
    assert update_resp.get_json()['service']['prix'] == max_price

    # 4. Delete Service
    delete_resp = client.delete(f'/api/pros/services/{service_id}', headers=pro_auth_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.get_json()['message'] == 'Service supprimé avec succès'

    # Verify Deletion
    get_again = client.get('/api/pros/services', headers=pro_auth_headers)
    services_after = get_again.get_json()['services']
    assert len(services_after) == 0

def test_access_denied_for_client(client, app):
    """Test that a client cannot manage services."""
    with app.app_context():
        user = User(email='client@services.com', password='pw', role='client', nom='C', prenom='C', telephone='111')
        db.session.add(user)
        db.session.commit()
    
    login_resp = client.post('/api/auth/connexion', json={'email': 'client@services.com', 'password': 'pw'})
    token = login_resp.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    resp = client.post('/api/pros/services', json={'nom': 'Hack'}, headers=headers)
    assert resp.status_code == 403
