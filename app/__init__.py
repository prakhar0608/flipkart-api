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
        # Load from FLASK_ENV if available, default to 'default'
        config_name = os.environ.get('FLASK_ENV', 'default')
        
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    logger.info(f"Flask App initialized under environment: {config_name}")
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    return app
