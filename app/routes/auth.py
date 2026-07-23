from flask import Blueprint, request, jsonify, redirect
from app.services.auth_service import AuthService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """
    Initiates the Flipkart OAuth authorization flow.
    Generates a secure state, stores it in session, and redirects to Flipkart.
    """
    logger.info("Redirecting user to Flipkart Login Authorization URL...")
    try:
        login_url, state = AuthService.generate_login_url()
        # Log flow progression safely without printing credentials
        logger.info(f"Oauth login URL generated successfully. Flow state initialized.")
        return redirect(login_url)
    except Exception as e:
        logger.error(f"Failed to generate login URL: {e}")
        return jsonify({
            "message": "Internal server error occurred when starting authentication flow",
            "error": str(e)
        }), 500

@auth_bp.route('/callback')
def callback():
    """
    Handles redirect callback from Flipkart.
    Validates state token, checks for errors, and exchanges code for credentials.
    """
    logger.info("Received callback request from Flipkart OAuth.")
    
    # 1. Capture query parameters
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    state = request.args.get('state')
    code = request.args.get('code')
    
    # 2. Check for OAuth errors returned from Flipkart (e.g. user cancelled)
    if error:
        logger.warning(f"OAuth error received from provider: {error} - {error_description}")
        return jsonify({
            "message": "Authorization denied or failed from provider",
            "error": error,
            "description": error_description
        }), 400
        
    # 3. Validate state parameter (Anti-CSRF)
    if not AuthService.validate_state(state):
        logger.warning("Callback rejected: State parameter validation failed.")
        return jsonify({
            "message": "CSRF validation failed or session expired",
            "error": "invalid_state"
        }), 400
        
    # 4. Check for missing authorization code
    if not code:
        logger.warning("Callback rejected: Missing authorization code parameter.")
        return jsonify({
            "message": "Authorization failed: No authorization code was returned",
            "error": "missing_code"
        }), 400
        
    # 5. Exchange code for access & refresh tokens
    try:
        logger.info("Processing token exchange using authorization code...")
        token_data = AuthService.exchange_code_for_token(code)
        
        # Log successful completion without dumping actual secret keys
        logger.info("Token exchange completed successfully.")
        
        return jsonify({
            "message": "OAuth Authentication completed successfully!",
            "token_details": {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "expires_in": token_data.get("expires_in"),
                "token_type": token_data.get("token_type")
            }
        })
        
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return jsonify({
            "message": "Failed to exchange authorization code for tokens",
            "error": str(e)
        }), 400
