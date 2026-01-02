from flask_mail import Message
from app import mail
from flask import current_app
from app.models.service import Service
from app.services.logger import logger

# fonction centrale d'envoie de courriel
def envoyer_email(to, subject, html_body):
    # Fonction générique pour envoyer l'email
    try:
        msg = Message(
            subject=subject,
            recipients=[to],
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Erreur  lors de l'envoie du mail: {str(e)}")
        return False
    
# envoie du mail de confirmation de rendez vous
def envoyer_confirmation_rdv(appointment):
    # email de confirmation
    try:

        client = appointment.client
        pro = appointment.pro
        service = Service.query.get(appointment.service_id)

        # formatage de la date et de l'heure
        date_str = appointment.date.strftime('%d/%m/%Y')
        heure_debut = appointment.heure_debut.strftime('%H:%M')
        heure_fin = appointment.heure_fin.strftime('%H:%M')

        # sujet du courriel
        subject = f"Confirmation de reservation chez: {pro.business_name}"

        # Corps HTML
        html = f"""
        <h2>Réservation confirmée !</h2>
        <p>Bonjour {client.prenom},</p>
        <p>Votre rendez-vous a été confirmé avec succès.</p>
        
        <h3>Détails de votre réservation :</h3>
        <ul>
            <li><strong>Service :</strong> {service.nom}</li>
            <li><strong>Date :</strong> {date_str}</li>
            <li><strong>Heure :</strong> {heure_debut} - {heure_fin}</li>
            <li><strong>Durée :</strong> {service.duree_minutes} minutes</li>
            <li><strong>Lieu :</strong> {pro.adresse_salon}, {pro.ville}, {pro.province}{f', {pro.code_postal}' if pro.code_postal else ''}, {pro.pays}</li>
            <li><strong>Prix :</strong> {appointment.prix_total}$</li>
        </ul>
        
        <p>Nous avons hâte de vous accueillir !</p>
        <p>Cordialement,<br>L'équipe {pro.business_name}</p>
        """

        return envoyer_email(client.email, subject, html)
    
    except Exception as e:
        logger.error(f"Erreur envoie de mail de confirmation de rendez vous:\n- Client: {client.prenom} {client.nom} \n - Salon: {pro.business_name}\n - Service: {service.nom}\n Erreur: {str(e)}")
        return False
    
# envoie du mail de rappel de rendez vous
def envoyer_rappel_rdv(appointment):
    try:
        
        client = appointment.client
        pro = appointment.pro
        service = Service.query.get(appointment.service_id)
        
        date_str = appointment.date.strftime('%d/%m/%Y')
        heure_debut = appointment.heure_debut.strftime('%H:%M')
        
        subject = f"Rappel : Rendez-vous demain chez {pro.business_name}"
        
        html = f"""
        <h2>N'oubliez pas votre rendez-vous !</h2>
        <p>Bonjour {client.prenom},</p>
        <p>Nous vous rappelons que vous avez rendez-vous <strong>demain</strong> :</p>
        
        <ul>
            <li><strong>Service :</strong> {service.nom}</li>
            <li><strong>Date :</strong> {date_str}</li>
            <li><strong>Heure :</strong> {heure_debut}</li>
            <li><strong>Lieu :</strong> {pro.adresse_salon}, {pro.ville}, {pro.province}{f', {pro.code_postal}' if pro.code_postal else ''}, {pro.pays}</li>
        </ul>
        
        <p>À demain !</p>
        <p>Cordialement,<br>{pro.business_name}</p>
        """
        
        return envoyer_email(client.email, subject, html)
        
    except Exception as e:
        logger.error(f"Erreur envoie de mail de rappel de rendez vous:\n- Client: {client.prenom} {client.nom} \n - Salon: {pro.business_name}\n - Service: {service.nom}\n Erreur: {str(e)}")
        return False


# envoie de mail d'annulation de rendez vous
def envoyer_annulation_rdv(appointment, cancelled_by_role):
    #Envoie email d'annulation au client et au pro
    try:
        client = appointment.client
        pro = appointment.pro
        service = Service.query.get(appointment.service_id)
        
        date_str = appointment.date.strftime('%d/%m/%Y')
        heure_debut = appointment.heure_debut.strftime('%H:%M')
        
        subject = f"Annulation de votre rendez-vous chez {pro.business_name}"
        
        # Message différent selon qui annule
        if cancelled_by_role == 'client':
            message = "Vous avez annulé votre rendez-vous."
        else:
            message = "Nous sommes désolés, mais votre rendez-vous a été annulé par le professionnel."
        
        html = f"""
        <h2>Annulation de rendez-vous</h2>
        <p>Bonjour {client.prenom},</p>
        <p>{message}</p>
        
        <h3>Détails du rendez-vous annulé :</h3>
        <ul>
            <li><strong>Service :</strong> {service.nom}</li>
            <li><strong>Date :</strong> {date_str}</li>
            <li><strong>Heure :</strong> {heure_debut}</li>
        </ul>
        
        <p>Vous pouvez prendre un nouveau rendez-vous quand vous le souhaitez.</p>
        <p>Cordialement,<br>{pro.business_name}</p>
        """
        
        # Envoyer au client
        envoyer_email(client.email, subject, html)
        
        # Envoyer au pro aussi
        subject_pro = f"RDV annulé - {client.prenom} {client.nom}"
        html_pro = f"""
        <h2>Rendez-vous annulé</h2>
        <p>Le rendez-vous suivant a été annulé :</p>
        <ul>
            <li><strong>Client :</strong> {client.prenom} {client.nom}</li>
            <li><strong>Service :</strong> {service.nom}</li>
            <li><strong>Date :</strong> {date_str}</li>
            <li><strong>Heure :</strong> {heure_debut}</li>
        </ul>
        """
        envoyer_email(pro.user.email, subject_pro, html_pro)
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur envoie de mail d'annulation de rendez vous:\n- Client: {client.prenom} {client.nom} \n - Salon: {pro.business_name}\n - Service: {service.nom}\n Erreur: {str(e)}")
        return False


# envoie de l'email de verification de compte
def envoyer_mail_verification(destinataire, code):
    try:
        print("email")
        print(destinataire.email)
        subject = "Code de vérification Aster"
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">Vérifiez votre compte</h2>
            
            <p>Entrez ce code dans l'application :</p>
            
            <div style="background: #f4f4f4; border: 2px solid #007bff; border-radius: 8px; padding: 25px; text-align: center; margin: 20px 0;">
                <div style="font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #007bff;">{code}</div>
            </div>
            
            <p style="color: #666; font-size: 14px;">Valide pendant 10 minutes</p>
            
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                L'équipe Aster
            </p>
        </div>
        """
        
        envoyer_email(destinataire.email, subject, html)

    except Exception as e:
        logger.error(f"Erreur envoie de mail de verification d'adresse courriel:\n- Utilisateur: {destinataire.email}\n Erreur: {str(e)}")
        return False


# envoie de l'email de recuperation de mot de passe oublié
def envoyer_mail_recuperation_mot_de_passe(destinataire, lien):
    try:

        subject = "Réinitialisation mot de passe - Aster"
        html = f"""
            <h2>Réinitialisation de mot de passe</h2>
            <p>Bonjour {destinataire.prenom},</p>
            <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
            <p>Cliquez sur ce lien (valide 30 minutes) :</p>
            <p><a href="{lien}">{lien}</a></p>
            <p>Si vous n'avez pas demandé ceci, ignorez ce message.</p>
        """

        envoyer_email(destinataire.email, subject, html)

    except Exception as e:
        logger.error(f"Erreur envoie de mail de recuperation de mot de passe:\n- Utilisateur: {destinataire.email}\n Erreur: {str(e)}")
        return False

