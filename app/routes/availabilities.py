from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.availability import Availability
from datetime import datetime
availabilities_bp = Blueprint('dispo', __name__)


#===============================
# Créer horaire
#===============================
@availabilities_bp.route('/pros/availabilities', methods=['POST'])
@jwt_required()
def creer_horaire():

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        data = request.get_json()

        required_fields = ['jour_semaine', 'heure_debut', 'heure_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        if data['jour_semaine'] < 0 or data['jour_semaine'] > 6:
            return jsonify({'error': 'Le jour de la semaine n\'est pas valide'}), 400
        
        
        if datetime.strptime(data['heure_fin'], '%H:%M').time() < datetime.strptime(data['heure_debut'], '%H:%M').time():
            return jsonify({'error': 'L\'heure de début ne peut être supérieure a l\'heure de la fin'}), 400
        
        doublon = Availability.query.filter_by(
            pro_id=user.pro.id,
            jour_semaine=data['jour_semaine']
        ).first()

        if doublon:
            return jsonify({'error': 'Horaire déjà défini pour ce jour'}), 400

        availability = Availability(
            pro_id=user.pro.id,
            jour_semaine=data['jour_semaine'],
            heure_debut=datetime.strptime(data['heure_debut'], '%H:%M').time(),
            heure_fin=datetime.strptime(data['heure_fin'], '%H:%M').time(),
        )

        db.session.add(availability)
        db.session.commit()

        return jsonify({
            'message': 'Disponibilité créé avec succès',
            'availability': availability.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
 

@availabilities_bp.route('/pros/availabilities', methods=['GET'])
@jwt_required()
def lister_horaires():
    # lister les horaires
    # GET /api/pros/availabilities

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        #verifier si c'est un pro (le role)
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Verifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        availabilities = Availability.query.filter_by(pro_id=user.pro.id).order_by(Availability.jour_semaine).all()

        #convertion de chaque service en dictionnaire
        availability_list = [a.to_dict() for a in availabilities]

        return jsonify({'Disponibilités': availability_list}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@availabilities_bp.route('/pros/availabilities/<int:availability_id>', methods=['PUT'])
@jwt_required()
def modifier_horaire(availability_id) :

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        #verifier si c'est un pro ( le role)
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Verifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # recuperation de la disponibilite
        availability = Availability.query.get(availability_id)

        if not availability:
            return jsonify({'error': 'Disponibilité innexistante'}), 404
        
        # verifier si le disponibilite appartient au pro
        if availability.pro_id != user.pro.id :
            return jsonify({'error': 'Vous n\'avez pas les droits necessaires pour effectuer cette opération'}), 403
        
        data = request.get_json()

        #Mise a jour
        if 'heure_debut' in data:
            availability.heure_debut =  datetime.strptime(data['heure_debut'], '%H:%M').time()
        if 'heure_fin' in data:
            availability.heure_fin = datetime.strptime(data['heure_fin'], '%H:%M').time()
        if 'is_active' in data:
            availability.is_active = data['is_active']

        if availability.heure_debut >= availability.heure_fin:
            return jsonify({'error': 'L\'heure de début doit être avant l\'heure de fin'}), 400

        db.session.commit()

        return jsonify({
            'message': 'Disponibilité modifié avec succès',
            'availability': availability.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    


@availabilities_bp.route('/pros/availabilities/<int:availability_id>', methods=['DELETE'])
@jwt_required()
def supprimer_horaire(availability_id):  

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

        # recuperation de la disponibilite
        availability = Availability.query.get(availability_id)

        if not availability:
            return jsonify({'error': 'Disponibilité innexistante'}), 404
        
        # verifier si le disponibilite appartient au pro
        if availability.pro_id != user.pro.id :
            return jsonify({'error': 'Vous n\'avez pas les droits necessaires pour effectuer cette opération'}), 403

        db.session.delete(availability)
        db.session.commit()

        return jsonify({'message': 'Disponibilité supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500