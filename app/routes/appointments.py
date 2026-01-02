from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.pro import Pro
from app.models.service import Service
from app.models.loyalty_account import LoyaltyAccount
from app.models.loyalty_history import LoyaltyHistory
from app.models.availability import Availability
from app.models.time_block import TimeBlock
from app.models.appointment import Appointment
from datetime import datetime, timedelta, timezone
from app.services.email import envoyer_confirmation_rdv, envoyer_rappel_rdv, envoyer_annulation_rdv
from app.services.logger import logger
from app.services.pagination import paginate
from app.services.geocoding import geocoder_adresse, calculer_distance


appointments_bp = Blueprint('rendez-vous', __name__ )


#===============================
# Créer un rendez vous
#===============================
@appointments_bp .route('/appointments', methods=['POST'])
@jwt_required()
def creer_rdv():

    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({'error': 'Compte utilisateur introuvable.'}), 401
        
        data = request.get_json()

        required_fields = ['pro_id', 'service_id', 'date', 'heure_debut', 'type_rdv']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Veuillez renseigner le champ obligatoire : {field}'}), 400
            
        # verification de l'existence du service
        service = Service.query.filter_by(id = data['service_id'], pro_id = data['pro_id']).first()

        if not service:
            return jsonify({'error': 'Ce service est indisponible ou non offert par ce professionnel.'}), 400
        
        # Vérifier que le service est disponible pour ce type
        if data['type_rdv'] == 'Salon' and not service.disponible_salon:
            return jsonify({'error': "Ce service n'est pas offert au salon."}), 400

        if data['type_rdv'] == 'Domicile' and not service.disponible_domicile:
            return jsonify({'error': "Ce service n'est pas offert à domicile."}), 400

        # Determination de l'heure de fin
        date_rdv = datetime.strptime(data['date'], '%Y-%m-%d').date()
        heure_debut = datetime.strptime(data['heure_debut'], '%H:%M').time()
        dt_debut = datetime.combine(date_rdv, heure_debut)
        dt_fin = dt_debut + timedelta(minutes=service.duree_minutes)
        heure_fin = dt_fin.time()        

        # Verification de la disponibilite du pro
        jour_semaine = date_rdv.weekday()
        availability_query = Availability.query.filter_by(
            pro_id = data['pro_id'],
            jour_semaine = jour_semaine,
            is_active = True
        )
        
        #if db.engine.name != 'sqlite':
            #availability_query = availability_query.with_for_update()
            
        availability = availability_query.first()

        if not availability:
            return jsonify({'error': 'Le professionnel est indisponible ce jour-là.'}), 400
        
        if heure_debut < availability.heure_debut or heure_fin > availability.heure_fin:
            return jsonify({'error': 'Cette plage horaire est en dehors des heures de disponibilité.'}), 400
        
        # Verifier si le professionnel n'a pas definis un time_blok sur cette periode
        block = TimeBlock.query.filter(
            TimeBlock.pro_id == data['pro_id'],
            TimeBlock.date_debut <= datetime.combine(date_rdv, heure_fin),
            TimeBlock.date_fin >= datetime.combine(date_rdv, heure_debut)
        ).first()

        if block:
            raison_msg = f" (Motif : {block.raison})" if block.raison else ""
            return jsonify({'error': f'Le professionnel est indisponible sur cette période.{raison_msg}'}), 400
        
        # Verifier si aucun autre rendez vous n'entre en conflit avec cette reservation
        conflit = Appointment.query.filter(
            Appointment.pro_id == data['pro_id'],
            Appointment.date == date_rdv,
            Appointment.statut.in_(['En attente', 'Confirmer']),
            Appointment.heure_debut < heure_fin,
            Appointment.heure_fin > heure_debut
        ).first()

        if conflit:
            return jsonify({'error': 'Cette plage horaire est déjà réservée.'}), 400
        
        # calcul du prix
        prix_total = service.prix
        prix_deplacement = 0
        distance_km = None

        if data['type_rdv'] == 'Domicile':
            if 'adresse_domicile' not in data:
                return jsonify({'error': 'L\'adresse de votre domicile est requise pour ce type de rendez-vous'}), 400

            lat_client, lng_client = geocoder_adresse(data['adresse_domicile'])

            if not lat_client or not lng_client:
                return jsonify({'error': 'Votre adresse est introuvable'}), 400
            
            pro = Pro.query.get(data['pro_id'])
            if not pro.latitude or not pro.longitude:
                return jsonify({'error': 'L\'adresse du professionnel n\'existe pas'}), 500
            
            distance_km = calculer_distance(
                pro.latitude, pro.longitude,
                lat_client, lng_client
            )

            if distance_km > pro.distance_max_km:
                return jsonify({'error': f'Vous êtes trop éloigné. La distance maximale est de: {pro.distance_max_km}km'}), 400

            tarif_km = current_app.config.get('TARIF_DEPLACEMENT_PAR_KM', 1.50)
            prix_deplacement = round(distance_km * 2 * tarif_km, 2)
            prix_total += prix_deplacement

        appointment = Appointment(
            client_id=user.id,
            pro_id=data['pro_id'],
            service_id=data['service_id'],
            date=date_rdv,
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            type_rdv=data['type_rdv'],
            prix_total=prix_total,
            prix_deplacement=prix_deplacement,
            distance_km=distance_km,
            notes_client=data.get('notes_client'),
            adresse_domicile=data.get('adresse_domicile') if data['type_rdv'] == 'Domicile' else None
        )


        db.session.add(appointment)
        db.session.commit()

        envoyer_confirmation_rdv(appointment)

        return jsonify({
            'message': 'Rendez-vous confirmé avec succès.',
            'reservation': appointment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500
 

#===============================
# Consulter tous les rendez vous
#===============================
@appointments_bp.route('/appointments', methods=['GET'])  
@jwt_required()
def lister_rdv():
    # recuperaion de l'identifiant de l'utilisateur connecte
    current_user_id = get_jwt_identity()
    user =User.query.get(int(current_user_id))
    
    if not user:
        return jsonify({'error': 'Compte utilisateur introuvable.'}), 401
    
    if user.role == 'client':
        query = Appointment.query.filter_by(client_id=user.id).order_by(
            Appointment.date.desc(), 
            Appointment.heure_debut.desc()
        )
    elif user.role == 'pro':
        if not user.pro:
            return jsonify({'error': 'Profil professionnel introuvable.'}), 404
        query = Appointment.query.filter_by(pro_id=user.pro.id).order_by(
            Appointment.date.desc(), 
            Appointment.heure_debut.desc()
        )

    result = paginate(query)

    # Ajouter flag alerte pour pro
    if user.role == 'pro':
        for rdv in result['items']:
            loyalty = LoyaltyAccount.query.filter_by(
                client_id=rdv['client_id'],
                pro_id=user.pro.id
            ).first()
            rdv['client_alerte_annulation'] = loyalty.late_cancellation_count >= 3 if loyalty else False

    return jsonify(result), 200

#===============================
# Consulter un rendez vous
#===============================
@appointments_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@jwt_required()
def details_rdv(appointment_id):

    # recuperaion de l'identifiant de l'utilisateur connecte
    current_user_id = get_jwt_identity()
    user =User.query.get(int(current_user_id))

    # recuperer le rendez vous dont on veut les informations
    appointment = Appointment.query.get(int(appointment_id))

    if not appointment:
        return jsonify({'error': 'Aucune information trouvée pour ce rendez-vous.'}), 404
    
    # verification des droits d'acces aux informations du rendez vous
    if user.role == 'client' and appointment.client_id != user.id:
        return jsonify({'error': 'Accès non autorisé.'}), 403

    if user.role == 'pro':
        if not user.pro or appointment.pro_id != user.pro.id:
            return jsonify({'error': 'Accès non autorisé.'}), 403
    
    return jsonify(appointment.to_dict()), 200 


#===============================
# Mettre a jour un rendez vous
#===============================
@appointments_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
def modifier_rdv(appointment_id):
    try:
        # recuperaion de l'identifiant de l'utilisateur connecte
        current_user_id = get_jwt_identity()
        user =User.query.get(int(current_user_id))

        # recuperer le rendez vous dont on veut les informations
        appointment = Appointment.query.get(int(appointment_id))

        if not appointment:
            return jsonify({'error': 'Aucune information trouvée pour ce rendez-vous.'}), 404
        
        # verification des droits d'acces aux informations du rendez vous
        if user.role == 'client' and appointment.client_id != user.id:
            return jsonify({'error': 'Accès non autorisé.'}), 403

        if user.role == 'pro':
            if not user.pro or appointment.pro_id != user.pro.id:
                return jsonify({'error': 'Accès non autorisé.'}), 403
        
        # Recuperer les nouvelles donnees a partir du formulaire
        data = request.get_json()
        nouveau_statut = data['statut']

        # Dans le cadre de la modification, un client peut juste faire une annulation 
        if user.role == 'client':
            if nouveau_statut != 'Annuler':
                return jsonify({'error': 'Vous ne pouvez pas effectuer cette opération.'}), 403
        
        if user.role == 'pro':
            # declarattion des differentes transition de statut valide
            transitions_valides = {
                'En attente': ['Confirmer', 'Annuler'], # un rdv en attente peut passer a confirmer ou annuler
                'Confirmer': ['Terminer', 'Annuler'], # un rdv confimer peut passer a terminer ou annuler
                'Terminer': [],  # un rdv terminer ne subira plus de changement
                'Annuler': []   # un rdv annuler ne subira plus de transitions
            }
        
            if nouveau_statut not in transitions_valides[appointment.statut]:
                return jsonify({'error': 'Changement de statut invalide.'}), 400
        
        # en cas d'annulation de rendez vous
        if nouveau_statut == 'Annuler':
            appointment.cancelled_by = user.id
            appointment.cancelled_at = datetime.now(timezone.utc)
            appointment.cancellation_reason = data.get('raison')
            cancelled_by_role = user.role
            envoyer_annulation_rdv(appointment, cancelled_by_role)

            # Vérifier si il s'agit d'une annulation tardive non conforme au reglement
            now = datetime.now(timezone.utc)
            rdv_datetime = datetime.combine(appointment.date, appointment.heure_debut, tzinfo=timezone.utc)   

            if rdv_datetime - now < timedelta(hours=2):
                appointment.is_late_cancellation = True
                loyalty = LoyaltyAccount.query.filter_by(
                    client_id=appointment.client_id,
                    pro_id=appointment.pro_id
                ).first()

                if loyalty:
                    loyalty.late_cancellation_count += 1
                    loyalty.last_late_cancellation = datetime.now(timezone.utc)
                else:
                    # Créer compte si existe pas
                    loyalty = LoyaltyAccount(
                        client_id=appointment.client_id,
                        pro_id=appointment.pro_id,
                        late_cancellation_count=1,
                        last_late_cancellation=datetime.now(timezone.utc)
                    )
                    db.session.add(loyalty)
                    
        # Mise a jour des points de fidelite
        if nouveau_statut  == 'Terminer' and appointment.statut!= 'Terminer':
            loyaltyAccount = LoyaltyAccount.query.filter_by(client_id =appointment.client_id, pro_id = appointment.pro_id).first()

            if not loyaltyAccount:
                loyaltyAccount = LoyaltyAccount(
                    client_id = appointment.client_id,
                    pro_id = appointment.pro_id,
                    points_total = 0,
                )
                db.session.add(loyaltyAccount)

            # recupere le service car chaque service a son nombre de point de fidelite
            service = Service.query.get(appointment.service_id)

            # ajouter les points au compte de fidelité
            loyaltyAccount.points_total += service.points_fidelite

            # creer une entrer dans l'historique
            loyaltyHistory = LoyaltyHistory(
                client_id = appointment.client_id,
                pro_id = appointment.pro_id,
                appointment_id = appointment_id,
                points_change = service.points_fidelite,
                raison = f'Rendez-vous terminé - {service.nom}'
            )

            db.session.add(loyaltyHistory)

        appointment.statut = nouveau_statut

        db.session.commit()

        return jsonify({
            'message': 'Rendez-vous modifié avec succès.',
            'Rendez vous': appointment.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur {request.endpoint}: {str(e)}")
        return jsonify({'error': str(e)}), 500 


