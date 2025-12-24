from .auth import auth_bp
from .services import services_bp
from .availabilities import availabilities_bp
from .time_blocks import time_blocks_bp
from .appointments import appointments_bp
from .portfolios import portfolios_bp

# Liste de tous les blueprints à enregistrer
__all__ = ['auth_bp', 'services_bp', 'availabilities_bp', 'time_blocks_bp', 'appointments_bp', 'portfolios_bp']