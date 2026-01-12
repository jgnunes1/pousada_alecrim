# config.py - VERSÃO CORRIGIDA E ORGANIZADA
import os
from datetime import timedelta
from urllib.parse import quote_plus

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ==================== SEGURANÇA ====================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'senha-super-secreta-pousada-2024'
    
    # ==================== BANCO DE DADOS ====================
    DB_HOST = 'localhost'
    DB_USER = 'pousada_admin'
    DB_PASSWORD = 'Pousada@2024'  # Contém @ - precisa ser codificado
    DB_NAME = 'pousada_alegrim'
    
    # Codificar senha (converte @ para %40 e outros caracteres especiais)
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD)
    
    # Database - usando SQLAlchemy (CORRIGIDO)
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}/{DB_NAME}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 10
        }
    }
    
    # ==================== UPLOAD DE ARQUIVOS ====================
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # ==================== SESSÃO ====================
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_COOKIE_SECURE = False  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ==================== INFORMAÇÕES DA POUSADA ====================
    POUSADA_NOME = "Pousada Alegrim"
    POUSADA_SLOGAN = "Conforto e sabor em Saquarema"
    POUSADA_DIFERENCIAL = "Oferecemos um rico café da manhã como parte da diária"
    POUSADA_ENDERECO = "Rua 95, nº 362 - Jaconé, Saquarema - RJ"
    POUSADA_TELEFONE = "(22) 99999-9999"
    POUSADA_EMAIL = "contato@pousadaalegrim.com"
    POUSADA_DESCRICAO = "Uma pousada acolhedora no coração de Saquarema, perfeita para quem busca descanso e contato com a natureza."
    
    # ==================== ADMINISTRAÇÃO ====================
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "pousada123"
    
    # ==================== EMAIL (opcional) ====================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # ==================== DEBUG/DEVELOPMENT ====================
    DEBUG = True
    TESTING = False