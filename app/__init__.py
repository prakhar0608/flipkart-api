import os
from flask import Flask
from app.config import config_by_name
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_app(config_name: str = None) -> Flask:
    """
    Application factory to create and configure the Flask app instance.
    """
    app = Flask(__name__)
    
    # Determine the configuration environment
    if not config_name:
        config_name = os.environ.get('FLASK_ENV', 'default')
        
    selected_config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(selected_config_class)
    
    logger.info(f"[DEBUG] Flask App initialized. FLASK_ENV/config_name: '{config_name}'. Config class loaded: {selected_config_class.__name__}")
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app
