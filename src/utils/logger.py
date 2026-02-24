import logging
import os
from datetime import datetime
from config.settings import settings

# Crear directorio de logs si no existe
os.makedirs(settings.LOGS_DIR, exist_ok=True)

# Configurar logging
log_filename = os.path.join(
    settings.LOGS_DIR, 
    f'hotel_system_{datetime.now().strftime("%Y%m%d")}.log'
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)