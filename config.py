# config.py - Configurações do banco e app
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'senha-super-secreta-pousada-alegrim-2024'
    
    # Configurações MySQL
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'pousada_admin'
    MYSQL_PASSWORD = 'Pousada@2024'
    MYSQL_DB = 'pousada_alegrim'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Configurações de upload (para fotos)
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max