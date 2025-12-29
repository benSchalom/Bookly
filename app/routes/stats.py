from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.appointment import Appointment
from app.models.loyalty_account import LoyaltyAccount
from sqlalchemy import func
from app import db

stats_bp = Blueprint('stats', __name__)

@stats_bp .route('/stats/pro', methods=['GET'])
@jwt_required()
def stats_pros():
    # Stats du professionnel
    # estimation de revenus, nombre de rendez vous annulés, nombre de rendez vous terminer, note ...
    try:    
         # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # calcul du nombre total de rendez vous
        total_rdv = Appointment.query.filter_by(pro_id=user.pro.id).count()
        # Nombre de rendez vous terminer
        total_termines = Appointment.query.filter_by(pro_id=user.pro.id, statut='Terminer').count()
        # Nombre de rendez ous annulé
        total_annules = Appointment.query.filter_by(pro_id=user.pro.id, statut='Annuler').count()
        # estimation de revenu total
        revenus_total = db.session.query(func.sum(Appointment.prix_total)).filter_by(
            pro_id=user.pro.id,
            statut='Terminer'
        ).scalar() or 0
        # taux d'annulation
        taux_annulation = (total_annules / total_rdv * 100) if total_rdv > 0 else 0

        return jsonify({
            'total_rdv': total_rdv,
            'total_termines': total_termines,
            'total_annules': total_annules,
            'revenus_total': float(revenus_total),
            'taux_annulation': round(taux_annulation, 2),
            'rating_avg': float(user.pro.rating_avg)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@stats_bp .route('/stats/clients', methods=['GET'])
@jwt_required()
def stats_clients():
    # stats des clients
    try:    
         # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'client':
            return jsonify({'error': 'Vous devez être connecté en tant que client'}), 403
    
        # Nombre total de rendez vous
        total_rdv = Appointment.query.filter_by(client_id=user.id).count()
        # points total tout pro confondus
        points_total = db.session.query(func.sum(LoyaltyAccount.points_total)).filter_by(
            client_id=user.id
        ).scalar() or 0
        # Annulation tardives
        late_cancellations = db.session.query(func.sum(LoyaltyAccount.late_cancellation_count)).filter_by(
            client_id=user.id
        ).scalar() or 0

        return jsonify({
            'total_rdv': total_rdv,
            'points_total_tous_pros': int(points_total),
            'late_cancellations_total': int(late_cancellations)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500