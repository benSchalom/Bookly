from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.pro import Pro
from app.models.service import Service
from app.models.portfolio import Portfolio
#from app.models.review import Review
from app.models.availability import Availability
from app import db

search_bp = Blueprint('search', __name__)

@search_bp.route('/pros/search', methods=['GET'])
def rechercher_pros():
        
    try:    
        # Récupération des paramètres
        ville = request.args.get('ville')
        specialite_id = request.args.get('specialite_id', type = int)
        business_name = request.args.get('business_name')

        # Requete
        # premiere partie : récupération des tous les pro (les infos)
        requete = Pro.query.join(User)

        # Deuxieme partie application des filtres
        if ville:
            requete = requete.filter(Pro.ville.ilike(f'%{ville}%')).order_by(Pro.created_at.desc())
        if specialite_id:
            requete = requete.filter(Pro.specialite_id == specialite_id).order_by(Pro.created_at.desc())
        if business_name:
            requete = requete.filter(Pro.business_name.ilike(f'%{business_name}%')).order_by(Pro.business_name.asc())

        pros = requete.limit(50).all()

        liste_pros = [pro.to_dict() for pro in pros]


        return jsonify({
            'pros': liste_pros,
            'count': len(liste_pros),
            'max_results': 50
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@search_bp.route('/pros/<int:pro_id>', methods=['GET'])
def profil_public_pro(pro_id):
    try:
        # verification de l'existence du pro
        pro = Pro.query.get(pro_id)

        if not pro:
            return jsonify ({'error': 'Désolé, mais nous n\'avons aucune information sur ce professionnel'}),404
        
        # Info lié au compte professionnel
        infos_pro = pro.to_dict()

        # Infos sur les services du pro
        services_pro = Service.query.filter_by(pro_id = pro_id, is_active = True).order_by(Service.ordre_affichage).all()
        liste_services = [service.to_dict() for service in services_pro] 

        # Infos sur le portfolio du pro
        portfolios_pro = Portfolio.query.filter_by(pro_id = pro_id).order_by(Portfolio.ordre_affichage).all()
        liste_portfolios = [p.to_dict() for p in portfolios_pro]

        # les 20 derniers avis sur le pro
        #avis_pro = Review.query.filter_by(pro_id = pro_id).order_by(Review.created_at.desc()).limit(20).all()
        #liste_avis = [a.to_dict() for a in avis_pro]

        # Disponibilité du pro
        disponibilites_pro = Availability.query.filter_by(pro_id = pro_id, is_active = True).order_by(Availability.jour_semaine).all()
        liste_disponibilites = [d.to_dict() for d in disponibilites_pro]

        return jsonify({
            'Pros': infos_pro,
            'Services': liste_services,
            'Portfolios': liste_portfolios,
            #'Avis': liste_avis,
            'Disponibilites': liste_disponibilites
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


        