import pytest
from datetime import datetime, timedelta
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.time_block import TimeBlock

@pytest.fixture
def management_setup(app, client):
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Pro
        spec = Specialite(nom='MgtSpec', slug='mgtspec')
        db.session.add(spec)
        pro_user = User(email='mgtpro@test.com', password='pw', role='pro', nom='P', prenom='P', telephone='111')
        db.session.add(pro_user)
        db.session.flush()
        pro = Pro(user_id=pro_user.id, business_name='MgtBiz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.flush()
        
        # Service
        svc = Service(pro_id=pro.id, nom='MgtSvc', duree_minutes=60, prix=50, is_active=True)
        db.session.add(svc)
        db.session.flush()
        
        # Availability (Everyday)
        t_start = datetime.strptime('09:00', '%H:%M').time()
        t_end = datetime.strptime('17:00', '%H:%M').time()
        
        for i in range(7):
             av = Availability(pro_id=pro.id, jour_semaine=i, heure_debut=t_start, heure_fin=t_end)
             db.session.add(av)

        # Client
        client_user = User(email='mgtclient@test.com', password='pw', role='client', nom='C', prenom='C', telephone='222')
        db.session.add(client_user)
        
        p_id = pro.id
        s_id = svc.id
        db.session.commit()
        
    # Login
    p_token = client.post('/api/auth/connexion', json={'email': 'mgtpro@test.com', 'password': 'pw'}).get_json()['access_token']
    c_token = client.post('/api/auth/connexion', json={'email': 'mgtclient@test.com', 'password': 'pw'}).get_json()['access_token']
    
    return {'pro_id': p_id, 'svc_id': s_id, 'p_token': p_token, 'c_token': c_token}

def test_stats_calculation(client, management_setup, app):
    """Test revenue and appointment stats."""
    pro_id = management_setup['pro_id']
    svc_id = management_setup['svc_id']
    
    # Create Appointments directly in DB to save time/mocking
    with app.app_context():
        t9 = datetime.strptime('09:00', '%H:%M').time()
        t10 = datetime.strptime('10:00', '%H:%M').time()
        t11 = datetime.strptime('11:00', '%H:%M').time()
        t12 = datetime.strptime('12:00', '%H:%M').time()
        t13 = datetime.strptime('13:00', '%H:%M').time()
        t14 = datetime.strptime('14:00', '%H:%M').time()
        
        # 1. Completed ($50)
        a1 = Appointment(client_id=2, pro_id=pro_id, service_id=svc_id, date=datetime.now().date(), heure_debut=t9, heure_fin=t10, type_rdv='Salon', prix_total=50, statut='Terminer')
        # 2. Completed ($50)
        a2 = Appointment(client_id=2, pro_id=pro_id, service_id=svc_id, date=datetime.now().date(), heure_debut=t10, heure_fin=t11, type_rdv='Salon', prix_total=50, statut='Terminer')
        # 3. Cancelled
        a3 = Appointment(client_id=2, pro_id=pro_id, service_id=svc_id, date=datetime.now().date(), heure_debut=t11, heure_fin=t12, type_rdv='Salon', prix_total=50, statut='Annuler')
        # 4. Pending
        a4 = Appointment(client_id=2, pro_id=pro_id, service_id=svc_id, date=datetime.now().date(), heure_debut=t13, heure_fin=t14, type_rdv='Salon', prix_total=50, statut='En attente')
        
        db.session.add_all([a1, a2, a3, a4])
        db.session.commit()
        
    # Get Stats
    resp = client.get('/api/stats/pro', headers={'Authorization': f'Bearer {management_setup["p_token"]}'})
    assert resp.status_code == 200
    stats = resp.get_json()
    
    assert stats['total_rdv'] == 4
    assert stats['total_termines'] == 2
    assert stats['total_annules'] == 1
    assert stats['revenus_total'] == 100.0 # 50 + 50
    assert stats['taux_annulation'] == 25.0

def test_time_blocks_interaction(client, management_setup):
    """Test blocking time and preventing appointments."""
    p_token = management_setup['p_token']
    c_token = management_setup['c_token']
    pro_id = management_setup['pro_id']
    svc_id = management_setup['svc_id']
    
    date_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_time = '12:00:00'
    end_time = '14:00:00'
    
    # 1. Create TimeBlock (12:00 - 14:00)
    resp = client.post('/api/pros/time-blocks', json={
        'date_debut': f'{date_str}T{start_time}',
        'date_fin': f'{date_str}T{end_time}',
        'raison': 'Lunch'
    }, headers={'Authorization': f'Bearer {p_token}'})
    assert resp.status_code == 201
    block_id = resp.get_json()['time_block']['id']
    
    # 2. Try to book appointment intersecting (11:30 - 12:30) ? Service is 60 min.
    # Start at 11:30 -> Ends 12:30. Overlaps with 12:00 start.
    resp = client.post('/api/appointments', json={
        'pro_id': pro_id,
        'service_id': svc_id,
        'date': date_str,
        'heure_debut': '11:30',
        'type_rdv': 'Salon'
    }, headers={'Authorization': f'Bearer {c_token}'})
    assert resp.status_code == 400
    assert 'Le professionnel est indisponible sur cette période.' in resp.get_json()['error']
    
    # 3. Delete TimeBlock
    client.delete(f'/api/pros/time-blocks/{block_id}', headers={'Authorization': f'Bearer {p_token}'})
    
    # 4. Try to book again (Should succeed)
    # Note: 11:30 might fail due to availability slots not matching exactly 60m blocks?
    # Availability is 09-17. 11:30 is fine.
    # But wait, availability check usually doesn't force aligned slots unless app logic does.
    # In `appointments.py`, it just checks `heure_debut < av.heure_debut or ...`.
    # And check for conflicts.
    resp = client.post('/api/appointments', json={
        'pro_id': pro_id,
        'service_id': svc_id,
        'date': date_str,
        'heure_debut': '11:30',
        'type_rdv': 'Salon'
    }, headers={'Authorization': f'Bearer {c_token}'})
    
    if resp.status_code != 201:
        print(resp.get_json())
    assert resp.status_code == 201
