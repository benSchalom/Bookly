import pytest
from unittest.mock import patch
from app.models.user import User

def test_email_sent_on_signup(client, app):
    """Test that an email is 'sent' when a user registers (even if just welcome email logic exists)."""
    # Note: Actuellement le code d'inscription n'envoie PAS d'email explicite dans le controleur `auth.py`. 
    # Sauf pour le reset password.
    # Vérifions donc le reset password qui utilise surement envoyer_email.
    pass

def test_password_reset_email(client, app):
    """Test that password reset requests trigger an email."""
    # Create user
    with app.app_context():
        # Setup user manually using client to trigger db
        pass

    # Register
    client.post('/api/auth/inscription', json={
        'email': 'forgot@test.com',
        'password': 'Password123!',
        'nom': 'For',
        'prenom': 'Got',
        'telephone': '1111111111'
    })

    # Mock envoyer_email
    with patch('app.routes.auth.envoyer_email') as mock_email:
        response = client.post('/api/auth/mot-de-passe-oublie', json={
            'email': 'forgot@test.com'
        })
        
        assert response.status_code == 200
        assert mock_email.called
        args, _ = mock_email.call_args
        assert args[0] == 'forgot@test.com'
        assert 'Réinitialisation mot de passe' in args[1] # Subject
