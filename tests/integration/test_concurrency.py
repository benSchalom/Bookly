import pytest
import concurrent.futures
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite
from app.models.service import Service
from app.models.availability import Availability
from datetime import datetime, timedelta, time

@pytest.fixture
def race_setup(app):
    """Setup for race condition test."""
    with app.app_context():
        # Clean db 
        db.drop_all()
        db.create_all()

        spec = Specialite(nom='RaceSpec', slug='racespec')
        db.session.add(spec)
        
        # Pro
        pro_user = User(email='racepro@test.com', password='pw', role='pro', nom='P', prenom='P', telephone='0')
        db.session.add(pro_user)
        db.session.flush() # get id
        
        pro = Pro(user_id=pro_user.id, business_name='RaceBiz', specialite_id=spec.id, adresse_salon='A', ville='V', pays='P', province='Pr')
        db.session.add(pro)
        db.session.flush()

        # Service
        service = Service(pro_id=pro.id, nom='RaceCut', duree_minutes=60, prix=10.0)
        db.session.add(service)

        # Avail (Everyday)
        avail = Availability(pro_id=pro.id, jour_semaine=datetime.now().weekday(), heure_debut=time(0,0), heure_fin=time(23,59))
        db.session.add(avail)

        db.session.commit()

        # 4 Clients
        tokens = []
        from flask_jwt_extended import create_access_token
        
        for i in range(4):
            email = f'racer{i}@test.com'
            user = User(
                email=email,
                password='Password123!',
                nom=f'Racer{i}',
                prenom='R',
                telephone=f'514123400{i}',
                role='client'
            )
            db.session.add(user)
            db.session.commit() # commit each to get ID
            
            token = create_access_token(identity=str(user.id))
            tokens.append(token)
            
        return {
            'pro_id': pro.id,
            'service_id': service.id,
            'tokens': tokens
        }

@pytest.mark.xfail(reason="SQLite does not support row-level locking (FOR UPDATE), so race conditions persist in tests.")
def test_booking_race_condition(app, race_setup):
    """Simulate 4 users booking exact same slot at exact same time."""
    pro_id = race_setup['pro_id']
    service_id = race_setup['service_id']
    tokens = race_setup['tokens']
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    heure_debut = '12:00'

    def make_booking_request(token):
        # Create a NEW client for each thread to avoid context errors if any
        # But Flask test client is thread local?? 
        # Actually with pytest-flask and app fixture, we can re-use app to make client
        client = app.test_client()
        resp = client.post('/api/appointments', json={
            'pro_id': pro_id,
            'service_id': service_id,
            'date': date_str,
            'heure_debut': heure_debut,
            'type_rdv': 'Salon'
        }, headers={'Authorization': f'Bearer {token}'})
        if resp.status_code == 500:
            print(f"500 Error: {resp.get_json()}")
        return resp.status_code

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(make_booking_request, token) for token in tokens]
        results = [f.result() for f in futures]

    # Analysis
    success_count = results.count(201)
    # In SQLite threaded tests, we might get 500 (InterfaceError) or 400 (if logic works fast)
    fail_count = results.count(400) + results.count(500)
    
    print(f"All Results: {results}")
    print(f"Race Results: Success={success_count}, Rejections={fail_count}")

    # Ideally only 1 should succeed. 
    # Note: With SQLite in-memory and python threads, true parallel race is hard to trigger 
    # because of GIL and SQLite locking. But if logic is not transactional, it might still allow 2.
    assert success_count == 1, f"Only 1 booking should succeed, got {success_count}"
    assert fail_count == 3, f"3 bookings should be rejected, got {fail_count}"
