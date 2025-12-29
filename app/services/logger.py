import logging
import os
from datetime import datetime

# Créer dossier logs si existe pas
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Config logger
logger = logging.getLogger('bookly')
logger.setLevel(logging.ERROR)

# Handler fichier
log_file = os.path.join(log_dir, 'errors.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)

# Format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)

# Ajouter handler au logger
logger.addHandler(file_handler)

# Éviter duplication des logs
logger.propagate = False