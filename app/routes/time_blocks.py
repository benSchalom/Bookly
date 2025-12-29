from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.time_block import TimeBlock
from datetime import datetime
from app.services.logger import logger

time_blocks_bp = Blueprint('time_blocks', __name__)


#===============================
# Créer blocage
#===============================
@time_blocks_bp.route('/pros/time-blocks', methods=['POST'])
@jwt_required()
def creer_blocage():

    try:
        # Récupération de l'utilisateur connecté
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        # Vérifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Vérifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        data = request.get_json()
        
        # Validation champs requis
        required_fields = ['date_debut', 'date_fin']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Convertir les dates ISO en datetime
        try:
            date_debut = datetime.fromisoformat(data['date_debut'].replace('Z', '+00:00'))
            date_fin = datetime.fromisoformat(data['date_fin'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utiliser ISO 8601 (ex: 2025-12-24T00:00:00)'}), 400
        
        # Valider date_debut < date_fin
        if date_debut >= date_fin:
            return jsonify({'error': 'La date de début doit être avant la date de fin'}), 400
        
        # Créer le blocage
        time_block = TimeBlock(
            pro_id=user.pro.id,
            date_debut=date_debut,
            date_fin=date_fin,
            raison=data.get('raison') 
        )
        
        db.session.add(time_block)
        db.session.commit()
        
        return jsonify({
            'message': 'Blocage créé avec succès',
            'time_block': time_block.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500


#===============================
# Lister blocages
#===============================
@time_blocks_bp.route('/pros/time-blocks', methods=['GET'])
@jwt_required()
def lister_blocages():

    try:
        # Récupération de l'utilisateur connecté
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        # Vérifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Vérifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # Récupérer les blocages du pro, triés par date_debut
        time_blocks = TimeBlock.query.filter_by(
            pro_id=user.pro.id
        ).order_by(TimeBlock.date_debut).all()
        
        # Convertir en liste de dictionnaires
        blocks_list = [block.to_dict() for block in time_blocks]
        
        return jsonify({'time_blocks': blocks_list}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#===============================
# Supprimer blocage
#===============================
@time_blocks_bp.route('/pros/time-blocks/<int:block_id>', methods=['DELETE'])
@jwt_required()
def supprimer_blocage(block_id):

    try:
        # Récupération de l'utilisateur connecté
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        # Vérifier si c'est un pro
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        # Vérifier si il a un profil pro
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # Récupérer le blocage
        time_block = TimeBlock.query.get(block_id)
        
        if not time_block:
            return jsonify({'error': 'Blocage inexistant'}), 404
        
        # Vérifier si le blocage appartient au pro
        if time_block.pro_id != user.pro.id:
            return jsonify({'error': 'Vous n\'avez pas les droits nécessaires pour effectuer cette opération'}), 403
        
        db.session.delete(time_block)
        db.session.commit()
        
        return jsonify({'message': 'Blocage supprimé avec succès'}), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500