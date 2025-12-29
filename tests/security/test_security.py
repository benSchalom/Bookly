import pytest
from app import db
from app.models.user import User

def test_rate_limiting(client, app):
    """Test protection against brute force (Rate Limiting)."""
    # Login endpoint has limit "5 per 10 minutes"
    
    # Register a user heavily to be sure we exist
    client.post('/api/auth/inscription', json={
        'email': 'ratelimit@test.com',
        'password': 'Password123!',
        'nom': 'Rate',
        'prenom': 'Limit',
        'telephone': '0000000000'
    })

    # Try to login 10 times
    limit_hit = False
    for i in range(10):
        response = client.post('/api/auth/connexion', json={
            'email': 'ratelimit@test.com',
            'password': 'WrongPassword'
        })
        if response.status_code == 429:
            limit_hit = True
            break
            
    assert limit_hit, "Rate limit should have been triggered (429 Too Many Requests)"

def test_sql_injection_attempt(client):
    """Test resilience against SQL Injection in login."""
    # Attempt SQL Injection in email field
    payloads = [
        "' OR '1'='1",
        "admin' --",
        "'; DROP TABLE users; --"
    ]
    
    for payload in payloads:
        response = client.post('/api/auth/connexion', json={
            'email': payload,
            'password': 'Password123!'
        })
        # Should be 401 (Unauthorized) or 400 (Bad Request), NOT 500 (Server Error)
        # And definitely NOT 200 (Success)
        assert response.status_code in [401, 400, 404]
        assert response.status_code != 500
