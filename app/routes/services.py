from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.service import Service
from app.models.user import User
from app.services.logger import logger

services_bp = Blueprint('services', __name__)

@services_bp.route('/pros/services', methods=['POST'])
@jwt_required()
def creer_service():
    # Creer un nouveau service (pour les pro)
    # POST  /pros/services
    # Headers: Authorization: Bearer <access_token>
    # Body{
    #    nom, description, duree_minutes, prix,
    #    disponible_salon, disponible_domicile, ordre_affichage 
    #}

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        data = request.get_json()

        required_fields = ['nom', 'duree_minutes', 'prix']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        if data['duree_minutes'] <= 0:
            return jsonify({'error': 'La durée doit être supérieure à 0'}), 400
        
        if data['prix'] <= 0:
            return jsonify({'error': 'Le prix doit être supérieur à 0'}), 400
        
        service = Service(
            pro_id=user.pro.id,
            nom=data['nom'],
            description=data.get('description'),  
            duree_minutes=data['duree_minutes'],
            prix=data['prix'],
            disponible_salon=data.get('disponible_salon', True),  
            disponible_domicile=data.get('disponible_domicile', False),  
            ordre_affichage=data.get('ordre_affichage', 0)  
        )

        db.session.add(service)
        db.session.commit()

        return jsonify({
            'message': 'Service créé avec succès',
            'service': service.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@services_bp.route('/pros/services', methods=['GET'])
@jwt_required()
def lister_mes_services():
    # liste des services offert par un pro
    # GET /api/pros/services
    # Headers: Authorization: Bearer <access_token>

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        #verifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Verifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        services = Service.query.filter_by(pro_id=user.pro.id).order_by(Service.ordre_affichage).all()

        #convertion de chaque service en dictionnaire
        services_list = [service.to_dict() for service in services]

        return jsonify({'services': services_list}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@services_bp.route('/pros/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def modifier_service(service_id):

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        #verifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Verifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # recuperation du service
        service = Service.query.get(service_id)

        if not service:
            return jsonify({'error': 'Service innexistant'}), 404
        
        #verifier si le service appartient au pro
        if service.pro_id != user.pro.id :
            return jsonify({'error': 'Vous n\'avez pas les droits necessaires pour effectuer cette opération'}), 403
        
        data = request.get_json()

        #Mise a jour
        if 'nom' in data:
            service.nom =  data['nom']
        if 'description' in data:
            service.description = data['description']
        if 'disponible_salon' in data:
            service.disponible_salon = data['disponible_salon']
        if 'disponible_domicile' in data:
            service.disponible_domicile = data['disponible_domicile']
        if 'is_active' in data:
            service.is_active = data['is_active']

        if 'duree_minutes' in data:
            if data['duree_minutes'] <= 0:
                return jsonify({'error': 'La durée doit être supérieure à 0'}), 400
            service.duree_minutes = data['duree_minutes']
        if 'prix' in data:
            if data['prix'] <= 0:
                return jsonify({'error': 'Le prix doit être supérieur à 0'}), 400
            service.prix = data['prix']

 
            db.session.commit()

            return jsonify({
                'message': 'Service modifié avec succès',
                'service': service.to_dict()
            }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@services_bp.route('/pros/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def supprimer_service(service_id):

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        #verifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Verifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404

        # recuperation du service
        service = Service.query.get(service_id)

        if not service:
            return jsonify({'error': 'Service innexistant'}), 404
        
        #verifier si le service appartient au pro
        if service.pro_id != user.pro.id :
            return jsonify({'error': 'Vous n\'avez pas les droits necessaires pour effectuer cette opération'}), 403
        
        db.session.delete(service)
        db.session.commit()

        return jsonify({'message': 'Service supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500