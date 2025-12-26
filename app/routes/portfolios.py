from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.portfolio import Portfolio
from app.models.user import User

portfolios_bp = Blueprint('portfolios', __name__)

@portfolios_bp.route('/pros/portfolios', methods=['POST'])
@jwt_required()
def ajouter_image():
    # Ajouter une photo au portfolio du pro
    # POST /api/pros/portfolios

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        nombre_images = Portfolio.query.filter_by(pro_id = user.pro.id).count()

        # Limitation du nombre de photo par pro vu que je suis en mode gratuit
        if nombre_images >=10:
            return jsonify({'error': 'Désolé, mais vous avez atteint votre limite de 10 photos sur votre portfolio'}), 400

        data = request.get_json()

        #Verifier si on a une image dans le formulaire
        if 'image_url' not in data:
            return jsonify({'error': 'Désolé, mais il manque l\'image à ajouter au portfolio'}), 400
        
        # creation du portfolio
        portfolio = Portfolio( 
            pro_id = user.pro.id,
            image_url = data['image_url'],
            description = data.get('description'),
            ordre_affichage = data.get('ordre_affichage', nombre_images)
        )

        db.session.add(portfolio)
        db.session.commit()

        return jsonify({
            'message': 'Portfolio créé avec succès',
            'Portfolio': portfolio.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

    
@portfolios_bp.route('/pros/<int:pro_id>/portfolios', methods=['GET'])
def lister_images(pro_id):
    # Liste publique de toutes les photos 
    # constituant le portfolio d'un coiffeur
    # Pas de vérification d'accès car accessible à tous

    try:

        #recuperation des images du pro
        list_photos = Portfolio.query.filter_by(pro_id = pro_id).order_by(Portfolio.ordre_affichage).all()

        # convertions en liste
        return jsonify({'images': [img.to_dict() for img in list_photos]}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



@portfolios_bp.route('/pros/portfolios/<int:image_id>', methods=['DELETE'])
@jwt_required()
def supprimer_image(image_id):

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user or user.role != 'pro':
            return jsonify({'error': 'Réservé aux professionnels'}), 403
        
        if not user.pro:
            return jsonify({'error': 'Profil professionnel non trouvé'}), 404
        
        # recuperer l'image a supprimer
        image = Portfolio.query.get(image_id)

        if not image:
            return jsonify ({'error': 'Désolé, vous ne pouvez pas effectué cette opération car l\'image n\existe pas'}), 404
        
        # verifiert si l'image appartient au pro
        if user.pro.id != image.pro_id:
            return jsonify ({'error': 'Vous n\'avez pas les autorisations pour effectuer cette opération'}), 403

        db.session.delete(image)
        db.session.commit()

        return jsonify({
            'message': 'Image supprimé avec succès',
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500