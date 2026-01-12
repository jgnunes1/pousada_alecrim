# routes/__init__.py
from .main import main_bp
from .admin import admin_bp
from .api import api_bp

def init_app(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api') 