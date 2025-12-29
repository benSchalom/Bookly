import pytest
from datetime import datetime
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.loyalty_account import LoyaltyAccount
from app.models.loyalty_history import LoyaltyHistory

@pytest.fixture
def loyalty_setup(app, client):
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Pro
        spec = Specialite(nom='LoyaltySpec', slug='loyaltyspec')
        db.session.add(spec)
        pro_user = User(email='loyaltypro@test.com', password='pw', role='pro', nom='P', prenom='P', telephone='111')
        db.session.add(pro_user)
        db.session.flush()
        pro = Pro(user_id=pro_user.id, business_name='LoyaltyBiz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.flush()
        
        # Service (10 points)
        svc = Service(pro_id=pro.id, nom='LoyaltySvc', duree_minutes=60, prix=50, points_fidelite=10, is_active=True)
        db.session.add(svc)
        db.session.flush()
        
        # Client
        client_user = User(email='loyaltyclient@test.com', password='pw', role='client', nom='C', prenom='C', telephone='222')
        db.session.add(client_user)
        db.session.flush()
        
        # Create Completed Appointment (Triggers Loyalty Logic in appointments.py? No, only API triggers it)
        # OR we can manually create Loyalty records to test the GET endpoints.
        # Since we tested appointment completion logic earlier (or assumed it works), 
        # let's test that if we complete an appointment via API, points are added.
        # But that requires full auth flow.
        # To keep it simple/focused on Loyalty endpoints, I will manually create LoyaltyAccount and History records.
        
        acc = LoyaltyAccount(client_id=client_user.id, pro_id=pro.id, points_total=50)
        db.session.add(acc)
        
        hist = LoyaltyHistory(client_id=client_user.id, pro_id=pro.id, appointment_id=None, points_change=10, raison='Bonus')
        db.session.add(hist)
        
        db.session.commit()
        
        c_id = client_user.id
        p_id = pro.id
        
    # Login Client
    c_token = client.post('/api/auth/connexion', json={'email': 'loyaltyclient@test.com', 'password': 'pw'}).get_json()['access_token']
    
    return {'client_id': c_id, 'pro_id': p_id, 'c_token': c_token}

def test_loyalty_endpoints(client, loyalty_setup):
    """Test fetching loyalty accounts and history."""
    c_token = loyalty_setup['c_token']
    pro_id = loyalty_setup['pro_id']
    
    # 1. Get Accounts
    resp = client.get('/api/loyalty/accounts', headers={'Authorization': f'Bearer {c_token}'})
    assert resp.status_code == 200
    data = resp.get_json()['Compte de fidélité']
    assert len(data) == 1
    assert data[0]['points_total'] == 50
    assert data[0]['business_name'] == 'LoyaltyBiz'
    
    # 2. Get History
    resp = client.get(f'/api/loyalty/history/{pro_id}', headers={'Authorization': f'Bearer {c_token}'})
    assert resp.status_code == 200
    data = resp.get_json()['Historique de fidélité']
    assert len(data) == 1
    assert data[0]['points_change'] == 10
    assert data[0]['raison'] == 'Bonus'
