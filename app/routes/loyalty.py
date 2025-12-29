from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.loyalty_account import LoyaltyAccount
from app.models.loyalty_history import LoyaltyHistory
from app import db

loyalty_bp = Blueprint('loyalty', __name__ )

@loyalty_bp.route('/loyalty/accounts', methods=['GET'])
@jwt_required()
def lister_comptes_loyalty():
    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'Compte utilisateur introuvable.'}), 401

        if user.role != 'client':
            return jsonify({'error': 'Cette fonctionnalité est réservée aux clients.'}), 403
        
        # Recuperation de tous les comptes de fidelité du client peu importe le pro
        comptes_fidelites = LoyaltyAccount.query.filter_by(client_id = user.id).all()

        # conversion en liste
        liste_comptes =[compte.to_dict() for compte in comptes_fidelites ]

        return jsonify({'Compte de fidélité': liste_comptes}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


@loyalty_bp.route('/loyalty/history/<int:pro_id>', methods=['GET'])
@jwt_required()
def lister_historque(pro_id):
    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'Compte utilisateur introuvable.'}), 401

        if user.role != 'client':
            return jsonify({'error': 'Cette fonctionnalité est réservée aux clients.'}), 403
        
        history = LoyaltyHistory.query.filter_by(client_id = user.id, pro_id = pro_id).order_by(LoyaltyHistory.created_at.desc()).all()

        liste_history = [his.to_dict() for his in history] 

        return jsonify({'Historique de fidélité': liste_history}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    