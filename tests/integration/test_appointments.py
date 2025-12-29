from datetime import datetime, timedelta, time
import pytest
from app import db
from app.models.specialite import Specialite
from app.models.availability import Availability
from app.models.service import Service
from app.models.user import User
from app.models.pro import Pro

@pytest.fixture
def booking_data(app):
    """Setup data for booking tests."""
    with app.app_context():
        # Specialite
        spec = Specialite(nom='Coiffure', slug='coiffure')
        db.session.add(spec)
        db.session.flush()

        # Pro User
        pro_user = User(email='pro@rdv.com', password='pw', role='pro', nom='P', prenom='P', telephone='000')
        db.session.add(pro_user)
        db.session.flush()

        # Pro Profile
        pro = Pro(user_id=pro_user.id, business_name='Biz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.flush()

        # Service
        service = Service(pro_id=pro.id, nom='Cut', duree_minutes=60, prix=50.0, disponible_salon=True)
        db.session.add(service)
        db.session.flush()

        # Availability (Monday 9-17h)
        avail = Availability(pro_id=pro.id, jour_semaine=0, heure_debut=time(9,0), heure_fin=time(17,0))
        db.session.add(avail)
        
        # Client User
        client_user = User(email='client@rdv.com', password='pw', role='client', nom='C', prenom='C', telephone='111')
        db.session.add(client_user)
        db.session.commit()
        
        return {
            'pro_id': pro.id,
            'service_id': service.id
        }

def test_appointment_lifecycle(client, booking_data):
    """Test full cycle: Create -> List -> Cancel."""
    
    # 1. Login Client
    login_resp = client.post('/api/auth/connexion', json={'email': 'client@rdv.com', 'password': 'pw'})
    token = login_resp.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Calculate date (Next Monday)
    today = datetime.now()
    days_ahead = 0 - today.weekday()
    if days_ahead <= 0: 
        days_ahead += 7
    next_monday = today + timedelta(days=days_ahead)
    date_str = next_monday.strftime('%Y-%m-%d')

    # 3. Create Appointment
    response = client.post('/api/appointments', json={
        'pro_id': booking_data['pro_id'],
        'service_id': booking_data['service_id'],
        'date': date_str,
        'heure_debut': '10:00',
        'type_rdv': 'Salon'
    }, headers=headers)

    assert response.status_code == 201, f"Error: {response.get_json()}"
    rdv_id = response.get_json()['reservation']['id']

    # 4. List Appointments
    list_resp = client.get('/api/appointments', headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.get_json()['items']
    assert len(items) >= 1
    assert items[0]['id'] == rdv_id

    # 5. Cancel Appointment
    cancel_resp = client.put(f'/api/appointments/{rdv_id}', json={
        'statut': 'Annuler',
        'raison': 'Changed mind'
    }, headers=headers)
    
    assert cancel_resp.status_code == 200
    assert cancel_resp.get_json()['Rendez vous']['statut'] == 'Annuler'

def test_appointment_unavailable_time(client, booking_data):
    """Test booking at unavailable time (Sunday)."""
    # Login
    login_resp = client.post('/api/auth/connexion', json={'email': 'client@rdv.com', 'password': 'pw'})
    token = login_resp.get_json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # Next Sunday
    today = datetime.now()
    days_ahead = 6 - today.weekday()
    if days_ahead <= 0: days_ahead += 7
    next_sunday = today + timedelta(days=days_ahead)
    date_str = next_sunday.strftime('%Y-%m-%d')

    # Try Create
    response = client.post('/api/appointments', json={
        'pro_id': booking_data['pro_id'],
        'service_id': booking_data['service_id'],
        'date': date_str,
        'heure_debut': '10:00',
        'type_rdv': 'Salon'
    }, headers=headers)

    assert response.status_code == 400
    assert 'Le professionnel est indisponible ce jour-là.' in response.get_json()['error']
