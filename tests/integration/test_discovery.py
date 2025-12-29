import pytest
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.specialite import Specialite
from app.models.service import Service
from app.models.portfolio import Portfolio

@pytest.fixture
def discovery_setup(app):
    with app.app_context():
        # Clean
        db.drop_all()
        db.create_all()
        
        # Specs
        s1 = Specialite(nom='Hair', slug='hair')
        s2 = Specialite(nom='Nails', slug='nails')
        db.session.add_all([s1, s2])
        db.session.commit()
        
        # Pro 1 (Montreal, Hair, "Super Cuts")
        u1 = User(email='p1@t.com', password='pw', role='pro', nom='P1', prenom='P1', telephone='111')
        db.session.add(u1)
        db.session.flush()
        p1 = Pro(user_id=u1.id, business_name='Super Cuts', specialite_id=s1.id, adresse_salon='A', ville='Montreal', pays='Ca', province='QC')
        db.session.add(p1)
        db.session.flush()
        
        # Pro 2 (Quebec, Nails, "Nail Art")
        u2 = User(email='p2@t.com', password='pw', role='pro', nom='P2', prenom='P2', telephone='222')
        db.session.add(u2)
        db.session.flush()
        p2 = Pro(user_id=u2.id, business_name='Nail Art', specialite_id=s2.id, adresse_salon='B', ville='Quebec', pays='Ca', province='QC')
        db.session.add(p2)
        db.session.flush()
        
        # Data for Pro 1 Profile
        svc = Service(pro_id=p1.id, nom='Cut', duree_minutes=30, prix=10)
        db.session.add(svc)
        folio = Portfolio(pro_id=p1.id, image_url='img.jpg')
        db.session.add(folio)
        
        db.session.commit()
        
        return {'s1_id': s1.id, 's2_id': s2.id, 'p1_id': p1.id}

def test_search_features(client, discovery_setup):
    """Test search filters."""
    
    # 1. Search by City
    resp = client.get('/api/pros/search?ville=Montreal')
    assert resp.status_code == 200
    data = resp.get_json()['items'] # paginate returns items
    assert len(data) == 1
    assert data[0]['business_name'] == 'Super Cuts'
    
    # 2. Search by Business Name
    resp = client.get('/api/pros/search?business_name=Nail')
    assert resp.status_code == 200
    data = resp.get_json()['items']
    assert len(data) == 1
    assert data[0]['business_name'] == 'Nail Art'
    
    # 3. Search by Speciality
    s1_id = discovery_setup['s1_id']
    resp = client.get(f'/api/pros/search?specialite_id={s1_id}')
    assert resp.status_code == 200
    data = resp.get_json()['items']
    assert len(data) == 1
    assert data[0]['business_name'] == 'Super Cuts'
    
    # 4. No results
    resp = client.get('/api/pros/search?ville=Paris')
    data = resp.get_json()['items']
    assert len(data) == 0

def test_public_profile_aggregation(client, discovery_setup):
    """Test that public profile returns all aggregated data."""
    p1_id = discovery_setup['p1_id']
    
    resp = client.get(f'/api/pros/{p1_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert 'Pros' in data
    assert 'Services' in data
    assert 'Portfolios' in data
    assert 'Avis' in data
    assert 'Disponibilites' in data
    
    assert data['Pros']['business_name'] == 'Super Cuts'
    assert len(data['Services']) == 1
    assert len(data['Portfolios']) == 1
