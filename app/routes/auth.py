# Routes Auth pour Authentification
from app.services.validators import validation_email, validation_phone, validation_mot_de_passe
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db, limiter
from app.models import User, Pro, Specialite
from app.models.password_reset_token import PasswordResetToken
from datetime import timedelta, datetime, timezone
from app.services.email import envoyer_mail_verification, envoyer_mail_recuperation_mot_de_passe
from app.services.logger import logger
from app.services.geocoding import geocoder_adresse
import random


auth_bp = Blueprint('auth', __name__)


#===============================
# Inscription client
#===============================
@auth_bp.route('/auth/inscription', methods = ['POST'])
@limiter.limit("5 per hour") 
def inscription_client():
    # Creer un compte client
    # POST /api/auth/inscription
    # Body: {email, password, nom, prenom, telephone}

    try:
        data = request.get_json()

        # Validation des champs requis
        required_fields = ['email', 'password', 'nom', 'prenom', 'telephone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
            
        # Validation email
        valide, erreur = validation_email(data['email'])
        if not valide:
            return jsonify({'error': erreur}), 400

        #verifier si l'email existe déjà
        if User.query.filter_by(email = data['email']).first():
            return jsonify({'error': 'Cette adresse courriel est déjà utilisée.'}), 400

        # Validation téléphone
        valide, erreur = validation_phone(data['telephone'])
        if not valide:
            return jsonify({'error': erreur}), 400
        
        #verifier unicite du numero de telephone
        if User.query.filter_by(telephone = data['telephone']).first():
            return jsonify({'error': 'Ce numéro de téléphone est déjà utilisé.'}), 400
        
        # Validation mot de passe
        valide, erreur = validation_mot_de_passe(data['password'])
        if not valide:
            return jsonify({'error': erreur}), 400
        
        #si tout est beau, on creer le user
        user = User(
            email = data['email'],
            password = data['password'],
            role = 'client',
            nom = data['nom'],
            prenom = data['prenom'],
            telephone = data['telephone']
        )

        user.verification_code = random.randint(1000, 9999)
        user.code_expires_at = datetime.now() + timedelta(minutes=10)

        db.session.add(user)
        db.session.commit()

        envoyer_mail_verification(user, user.verification_code) 

        return jsonify({
            'message': 'Compte créé. Vérifiez votre email.',
            'user_id': user.id,
            'email': user.email,
            'requires_verification': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
 
#===============================
# Inscription pro
#===============================
@auth_bp.route('/auth/inscription-pro', methods = ['POST'])
@limiter.limit("5 per hour") 
def inscription_pro():
    # Créer un compte pro
    # POST /api/auth/inscription-pro
    # Body: {email, password, nom, prenom, telephone, business_name, specialite_id, ville}

    try:
        data = request.get_json() #recuperation des données a partir du formulaire

        #Validation des champs requis
        required_fields = [
            'email', 
            'password', 
            'nom', 
            'prenom', 
            'telephone', 
            'business_name', 
            'specialite_id', 
            'pays', 
            'province', 
            'ville', 
            'adresse_salon',
            'travail_salon',
            'travail_domicile'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        # Validation email ( le format )
        valide, erreur = validation_email(data['email'])
        if not valide:
            return jsonify({'error': erreur}), 400
                     
        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cette adresse courriel est déjà utilisée.'}), 400

        # Validation téléphone
        valide, erreur = validation_phone(data['telephone'])
        if not valide:
            return jsonify({'error': erreur}), 400
        
        #verifier unicite du numero de telephone
        if User.query.filter_by(telephone = data['telephone']).first():
            return jsonify({'error': 'Ce numéro de téléphone est déjà utilisé.'}), 400
        
        # Validation mot de passe
        valide, erreur = validation_mot_de_passe(data['password'])
        if not valide:
            return jsonify({'error': erreur}), 400
                
        # Vérifier que la spécialité existe
        specialite = Specialite.query.get(data['specialite_id'])
        if not specialite:
            return jsonify({'error': 'Spécialité invalide.'}), 400
        
        # Si le pro fait du domicile, distance_max_km est obligatoire
        if data.get('travail_domicile') and 'distance_max_km' not in data:
            return jsonify({'error': 'Veuillez renseigner la distacne maximale pour les services a domicile'}), 400
        
        # determiner les coordonnes du salon
        adresse_complete = f"{data['adresse_salon']}, {data['ville']}, {data['province']}, {data['pays']}"
        lat, lng = geocoder_adresse(adresse_complete)

        if not lat or not lng:
            return jsonify({'error': 'Adresse introuvable'}), 400

        user= User(
            email = data['email'],
            password = data['password'],
            role = 'pro',
            nom = data['nom'],
            prenom = data['prenom'],
            telephone = data['telephone']
        )    

        user.verification_code = random.randint(1000, 9999)
        user.code_expires_at = datetime.now() + timedelta(minutes=10)
        
        db.session.add(user)
        db.session.flush() #Pour obtenir user.id avant commit

        pro= Pro(
            user_id = user.id,
            business_name=data['business_name'],
            specialite_id=data['specialite_id'],
            ville = data['ville'],
            adresse_salon = data['adresse_salon'],
            pays = data['pays'],
            province=data['province'],
            travail_salon=data['travail_salon'],    
            travail_domicile=data['travail_domicile'],
            distance_max_km=data.get('distance_max_km') if data.get('travail_domicile') else None,
            latitude = lat,
            longitude = lng,
            code_postal = data['code_postal']
        )

        # Gestion des champs optionnels
        if 'bio' in data:
            pro.bio = data['bio']

        db.session.add(pro)
        db.session.commit()

        envoyer_mail_verification(user, user.verification_code) 

        return jsonify({
            'message': 'Compte professionnel créé. Vérifiez votre email.',
            'user_id': user.id,
            'email': user.email,
            'requires_verification': True
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

#=======================================================
# verification de L'email grace au code envoyer par mail
#=======================================================
@auth_bp.route('/auth/verification-email', methods=['POST'])
def verify_email():
    try: 
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ["user_id", "code"]
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        user_id = data.get('user_id')
        entered_code = data.get('code')
        
        # Validation format du code (nombre uniquement)
        if not str(entered_code).isdigit():
            return jsonify({'error': 'Code invalide'}), 400
        
        entered_code = int(entered_code)
        
        # Récupérer l'utilisateur
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        # Vérifier tentatives
        if user.verification_attempts >= 3:
            return jsonify({'error': 'Trop de tentatives. Demandez un nouveau code'}), 429
        
        # Vérifier le code
        if user.verification_code == entered_code:
            if datetime.now() < user.code_expires_at:
                user.email_verified = True
                user.verification_code = None
                user.verification_attempts = 0  
                db.session.commit()

                access_token = create_access_token(identity=str(user.id))
                refresh_token = create_refresh_token(identity=str(user.id))

                response = {
                    'success': True,
                    'message': 'Email vérifié avec succès',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': user.to_dict()
                }

                if user.role == 'pro' and user.pro:
                    response['pro'] = user.pro.to_dict()

                return jsonify(response), 200
            else:
                return jsonify({'error': 'Code expiré'}), 400
        else:
            user.verification_attempts += 1  
            db.session.commit()
            return jsonify({'error': 'Code invalide'}), 400
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500


#==========================================
# re-envoyer le code de verification du mail
#==========================================
@auth_bp.route('/auth/envoyer-code', methods=['POST'])
def resend_code():
    try:
        data = request.get_json()
        
        # Validation
        if 'user_id' not in data:
            return jsonify({'error': 'Le champ user_id est requis'}), 400
        
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur introuvable'}), 404
        
        # Régénérer code
        user.verification_code = random.randint(1000, 9999)
        user.code_expires_at = datetime.now() + timedelta(minutes=10)
        user.verification_attempts = 0
        db.session.commit()
        
        # Envoyer email
        envoyer_mail_verification(user, user.verification_code)
        
        return jsonify({'message': 'Code renvoyé'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500


#===============================
# Connexion
#===============================
@auth_bp.route('/auth/connexion', methods=['POST'])
@limiter.limit("3 per 10 minutes") 
def connexion():
    # se connecter
    # POST /api/auth/connexion
    # Body: {email, password}

    try:
        data = request.get_json()

        # Validation
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Cherchons le user
        user = User.query.filter_by(email = data['email']).first()

        # veifier que le user existe puis verifier le mot de passe
        if not user or not user.check_password(data['password']):
            return jsonify({'error': "L'adresse courriel ou le mot de passe est invalide."}), 401
        
        if not user.email_verified:
            return jsonify({
                'error': 'Veuillez vérifier votre email avant de vous connecter.',
                'requires_verification': True,
                'user_id': user.id
            }), 403
        
        if not user.is_active:
            return jsonify({'error': 'Votre compte est désactivé.'}), 403
        
        # Mettre a jour l'info sur la derniere connexion
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        # Generer les tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = {
            'message': 'Connexion réussie.',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        # Si c'est un pro, inclure les infos pro
        if user.role == 'pro' and user.pro:
            response['pro'] = user.pro.to_dict()

        return jsonify(response), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500


#===============================
# Recuperer l'utilisateur actuel
#===============================
@auth_bp.route('/auth/moi', methods=['GET'])
@jwt_required()
def utilisateur_actuel():
    # Récuperer l'utilisateur connecté
    # GET /api/auth/moi
    # Headers: Authorization: Bearer <acces_token>

    try:
        # recuperer l'id de l'utilisateur depuis le jwt
        current_user_id = get_jwt_identity()

        # recuperer le user
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'Compte utilisateur introuvable.'}), 404
        
        response = {
            'user': user.to_dict()
        }

        # inclusion des infos du pro
        if user.role == 'pro' and user.pro:
            response['pro'] = user.pro.to_dict()
        
        return jsonify(response), 200     
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# ============================================
# Rafraichissement du Token
# ============================================
@auth_bp.route('/auth/rafraichir', methods=['POST'])
@jwt_required(refresh=True)
def rafraichir():
    
    # Rafraîchir l'access token
    # POST /api/auth/rafraichir
    # Headers: Authorization: Bearer <refresh_token>

    try:
        # Récupérer l'ID du user depuis le refresh token
        current_user_id = get_jwt_identity()
        
        # Générer un nouveau access token
        new_access_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# Liste des specialités (pour le form register-pro)
# ============================================
@auth_bp.route('/auth/specialites', methods=['GET'])
def recuperer_specialites():

    # Liste toutes les spécialités
    # GET /api/auth/specialites
    try:
        specialites = Specialite.query.filter_by(is_active=True).order_by(Specialite.ordre_affichage).all()
        
        return jsonify({
            'specialites': [spec.to_dict() for spec in specialites]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# ============================================
# reset de mot de passe
# ============================================
@auth_bp.route('/auth/mot-de-passe-oublie', methods=['POST'])
@limiter.limit("5 per hour") 
def recuperation_mot_de_passe():
    try:
        data = request.get_json()
        if 'email' not in data:
            return jsonify({'error': 'Adresse courriel requise.'}), 400
        
        # chercher l'utilisateur
        user = User.query.filter_by(email=data['email']).first()

        # si l'utilisateur n'existe pas
        if not user:
            return jsonify({'message': 'Si cette adresse courriel existe, un lien a été envoyé.'}), 200
        
        # Marquer anciens tokens comme utilisés
        old_tokens = PasswordResetToken.query.filter_by(user_id=user.id, used=False).all()
        for token in old_tokens:
            token.used = True

        new_token = PasswordResetToken(
            user_id=user.id,
            token=PasswordResetToken.generate_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30)
        )
        db.session.add(new_token)

        reset_link = f"https://asteur.app/reset-password?token={new_token.token}"

        envoyer_mail_recuperation_mot_de_passe(user, reset_link)

        db.session.commit()

        return jsonify({'message': 'Si cet email existe, un lien a été envoyé'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
   

# ============================================
# reinitialiser le mot de passe
# ============================================
@auth_bp.route('/auth/reinitialiser-mot-de-passe', methods=['POST'])
@limiter.limit("5 per hour")
def reset_password():
    #Réinitialiser le mot de passe avec token
    try:
        data = request.get_json()
        
        # Validation champs requis
        required = ['token', 'new_password']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Veuillez renseigner le champ obligatoire : {field}'}), 400
        
        # Trouver token
        reset_token = PasswordResetToken.query.filter_by(token=data['token']).first()
        
        if not reset_token:
            return jsonify({'error': 'Jeton (token) invalide.'}), 400
        
        # Vérifier validité
        if not reset_token.is_valid():
            return jsonify({'error': 'Jeton (token) expiré ou déjà utilisé.'}), 400
        
        # Récupérer user
        user = User.query.get(reset_token.user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur introuvable.'}), 404
        
        # Validation nouveau mot de passe
        valide, erreur = validation_mot_de_passe(data['new_password'])
        if not valide:
            return jsonify({'error': erreur}), 400
        
        # Changer mot de passe
        user.set_password(data['new_password'])
        
        # Marquer token utilisé
        reset_token.used = True
        
        db.session.commit()
        
        return jsonify({'message': 'Mot de passe réinitialisé avec succès.'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500