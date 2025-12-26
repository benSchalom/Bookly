# Routes Auth pour Authentification

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Pro, Specialite

auth_bp = Blueprint('auth', __name__)


#===============================
# Inscription client
#===============================
@auth_bp.route('/auth/inscription', methods = ['POST'])
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
        
        #verifier si l'email existe déjà
        if User.query.filter_by(email = data['email']).first():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        #si tout est beau, on creer le user
        user = User(
            email = data['email'],
            password = data['password'],
            role = 'client',
            nom = data['nom'],
            prenom = data['prenom'],
            telephone = data['telephone']
        )

        db.session.add(user)
        db.session.commit()

        #Générer les tokens JWT
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Compte client crée avec succès',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

#===============================
# Inscription pro
#===============================
@auth_bp.route('/auth/inscription-pro', methods = ['POST'])
def inscription_pro():
    # Créer un compte pro
    # POST /api/auth/inscription-pro
    # Body: {email, password, nom, prenom, telephone, business_name, specialite_id, ville}

    try:
        data = request.get_json() #recuperation des données a partir du formulaire

        #Validation des champs requis
        required_fields = ['email', 'password', 'nom', 'prenom', 'telephone', 'business_name', 'specialite_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400

        # Vérifier si l'email existe déjà
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Cet email est déjà utilisé'}), 400
        
        # Vérifier que la spécialité existe
        specialite = Specialite.query.get(data['specialite_id'])
        if not specialite:
            return jsonify({'error': 'Spécialité invalide'}), 40 
        
        #important d,avoir une adresse adresse de salon meme si on a pas de salon (elle servira d,adresse de reference dans les calculs)
        if data.get('travail_domicile') and not data.get('adresse_salon'):
            return jsonify({
                'error': 'Adresse de référence requise pour travailler à domicile'
            }), 400

        user= User(
            email = data['email'],
            password = data['password'],
            role = 'pro',
            nom = data['nom'],
            prenom = data['prenom'],
            telephone = data['telephone']
        )    

        db.session.add(user)
        db.session.flush() #Pour obtenir user.id avant commit

        pro= Pro(
            user_id = user.id,
            business_name=data['business_name'],
            specialite_id=data['specialite_id']
        )

        # Gestion des champs optionnels
        if 'bio' in data:
            pro.bio = data['bio']
        if 'ville' in data:
            pro.ville = data['ville']
        if 'adresse_salon' in data:
            pro.adresse_salon = data['adresse_salon']

        db.session.add(pro)
        db.session.commit()

        # Générer les tokens JWT
        access_token = create_access_token(identity= str(user.id))
        refresh_token = create_refresh_token(identity= str(user.id))
        
        return jsonify({
            'message': 'Compte professionnel créé avec succès',
            'user': user.to_dict(),
            'pro': pro.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

#===============================
# Connexion
#===============================
@auth_bp.route('/auth/connexion', methods=['POST'])
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
        
        # Cherhons le user
        user = User.query.filter_by(email = data['email']).first()

        # veifier que le user existe pus verifier le mot de passe
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Votre compte est désactivé'}), 403
        
        # Mettre a jour l'info sur la derniere connexion
        from datetime import datetime, timezone
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        # Generer les tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = {
            'message': 'Connexion réussie',
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
            return jsonify({'error': 'Compte utilisateur non trouvé'}), 404
        
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