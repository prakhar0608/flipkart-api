from flask import Blueprint

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Returns a simple message to indicate the app is running.
    Useful for checking deployment status.
    """
    return "App is running"
