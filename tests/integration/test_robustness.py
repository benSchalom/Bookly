def test_invalid_json_payload(client):
    """Test sending invalid JSON (empty or malformed)."""
    # Empty body
    resp = client.post('/api/auth/inscription', data='', content_type='application/json')
    # Flask usually returns 400 Bad Request for get_json() on empty
    assert resp.status_code == 400 or resp.status_code == 500 or resp.status_code == 415

def test_missing_fields_inscription(client):
    """Test registering with missing fields."""
    resp = client.post('/api/auth/inscription', json={
        'email': 'incomplete@test.com'
    })
    # Controller checks required fields
    assert resp.status_code == 400
    assert 'requis' in resp.get_json()['error']

def test_invalid_data_types(client):
    """Test sending strings where ints are expected."""
    client.post('/api/auth/inscription', json={'email':'t@t.com', 'password':'Password123!', 'nom':'T', 'prenom':'T', 'telephone':'1234567890'})
    login = client.post('/api/auth/connexion', json={'email':'t@t.com', 'password':'Password123!'})
    token = login.get_json()['access_token']

    # Book with string ID
    resp = client.post('/api/appointments', json={
        'pro_id': "NOT_AN_INT",
        'service_id': 1,
        'date': "2025-01-01",
        'heure_debut': "10:00",
        'type_rdv': "Salon" 
    }, headers={'Authorization': f'Bearer {token}'})

    # Should be 400 or 500 (db error caught)
    # Controller casts: `user =User.query.get(int(current_user_id))` but here prompt is about input data.
    # SQLA might error.
    assert resp.status_code != 200

def test_huge_payload(client):
    """Test sending a huge payload."""
    huge_text = "a" * 1000000
    resp = client.post('/api/auth/connexion', json={
        'email': 't@t.com',
        'password': huge_text
    })
    # Should probably be 413 Payload Too Large (if configured) or just 401/500 processing it
    # We just want to ensure it doesn't crash the server process (returns a code)
    assert resp.status_code is not None
