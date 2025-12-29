from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.review import Review
from app.models.appointment import Appointment
from app.models.user import User
from app.models.pro import Pro


review_bp = Blueprint('reviews', __name__)

@review_bp.route('/reviews', methods=['POST'])
@jwt_required()
def creer_avis():
    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'Compte innexistant'}), 401
        
        if user.role != 'client':
            return jsonify({'error': 'Désolé, mais vous n\'avez pas les droits necessaires pour effectuer cette opération'}), 403
        
        data = request.get_json()

        required_fields = ['pro_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # validation de la note sur 5 
        if data['rating']< 1 or data['rating'] >5 :
            return jsonify({'error': 'La note doit être entre 1 et 5'}), 400
        
        # dans le cas ou il s'agit d'un avis specifique a un rdv
        if 'appointment_id' in data and data['appointment_id']:
            appointment = Appointment.query.get(data['appointment_id'])
            # Verifier si le rendez vous appartient au client
            if appointment.client_id != user.id:
                return jsonify({'error': 'Désolé, mais vous n\'avez pas les autorisations necessaires pour faire cette opération'}), 403

            if appointment.statut != 'Terminer':
                return jsonify({'error': 'Désolé, mais vous ne pouvew pas donné votre avis sur le rendez vous n\'est pas encore terminer'}), 400
        
        pro = Pro.query.get(data['pro_id'])

        review = Review(
            client_id= user.id,
            pro_id = pro.id,
            rating= data['rating'],
            commentaire = data.get('commentaire'),
            appointment_id = data.get('appointment_id')
        )

        # Recalculer la note
        reviews = Review.query.filter_by(pro_id = data['pro_id']).all()
        moyenne = sum([r.rating for r in reviews ])/ len(reviews) if len(reviews) > 0 else 1
        pro.rating_avg = moyenne

        db.session.add(review)
        db.session.commit()

        return jsonify({
            'message': 'Avis créé avec succès',
            'review': review.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@review_bp.route('/pros/<int:pro_id>/reviews', methods=['GET'])
def lister_avis_pro(pro_id):
    
    reviews = Review.query.filter_by(
        pro_id=pro_id
    ).order_by(Review.created_at.desc()).limit(20).all()
    
    liste_avis = [r.to_dict() for r in reviews]
    
    return jsonify({
        'reviews': liste_avis,
        'count': len(liste_avis)
    }), 200