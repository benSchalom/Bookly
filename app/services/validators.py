import re # regex
from datetime import datetime



def validation_email(email):
    # fonction de validation des emails

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Format email invalide"
    
    return True, None 


def validation_phone(phone):
    # Validation téléphone internationale

    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    # Vérifier que chiffres uniquement
    if not phone_clean.isdigit():
        return False, "Le numéro doit contenir uniquement des chiffres"
    
    # Longueur entre 10-15 chiffres (international)
    if len(phone_clean) < 10 or len(phone_clean) > 15:
        return False, "Numéro doit contenir entre 10 et 15 chiffres"
    
    return True, None



def validation_mot_de_passe(password):
    # taille superieur a 8
    if len(password) < 12:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    # Au moins une majuscule
    if not any(c.isupper() for c in password):
        return False, "Le mot de passe doit contenir au moins 1 majuscule"
    
    # Au moins une minuscule
    if not any(c.islower() for c in password):
        return False, "Le mot de passe doit contenir au moins 1 minuscule"
    
    # Au moins un chiffre
    if not any(c.isdigit() for c in password):
        return False, "Le mot de passe doit contenir au moins 1 chiffre"
    
    # Au moins un caractere special
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        return False, "Le mot de passe doit contenir au moins 1 caractère spécial"
   
    return True, None