from flask import Blueprint, request, render_template, current_app, session
from app.services.auth_service import AuthService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """
    Renders the login page containing the Flipkart Login SDK.
    Injects the required non-secret configurations (client_id, redirect_uri) 
    into the template for the SDK to initialize.
    """
    client_id = current_app.config.get('FLIPKART_CLIENT_ID')
    redirect_uri = current_app.config.get('FLIPKART_REDIRECT_URI')
    
    if not client_id or not redirect_uri:
        logger.error("Login route failed: Missing client_id or redirect_uri in configuration.")
        return render_template(
            'error.html', 
            error_title="Configuration Error",
            error_message="The application is missing required Flipkart configuration settings."
        ), 500

    logger.info("Rendering login page with Flipkart Login SDK.")
    return render_template(
        'login.html', 
        client_id=client_id, 
        redirect_uri=redirect_uri
    )

@auth_bp.route('/callback')
def callback():
    """
    Handles redirect callback from the Flipkart Login SDK.
    Exchanges the authorization code for tokens and securely stores them.
    
    SECURITY NOTE: State validation is bypassed here intentionally as the 
    Flipkart Login SDK does not expose a state parameter during initialization.
    Tokens are securely retained on the backend and NEVER sent to the frontend.
    """
    logger.info("Received callback request from Flipkart OAuth.")
    
    # 1. Capture query parameters
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    code = request.args.get('code')
    
    # 2. Check for OAuth errors returned from Flipkart
    if error:
        logger.warning(f"OAuth error received from provider: {error} - {error_description}")
        return render_template(
            'error.html',
            error_title="Authorization Failed",
            error_message=error_description or "The authorization request was denied or failed."
        ), 400
        
    # 3. Check for missing authorization code
    if not code:
        logger.warning("Callback rejected: Missing authorization code parameter.")
        return render_template(
            'error.html',
            error_title="Invalid Callback",
            error_message="No authorization code was provided by the authentication provider."
        ), 400
        
    # 4. Exchange code for access & refresh tokens
    try:
        logger.info("Processing token exchange using authorization code...")
        token_data = AuthService.exchange_code_for_token(code)
        
        # 5. Securely store tokens (delegated to AuthService)
        # We DO NOT expose these to the frontend
        # Currently using a dummy user_id 'default_user' since user authentication is not fully implemented
        AuthService.store_tokens('default_user', token_data)
        
        logger.info("Token exchange completed successfully. Tokens securely stored.")
        
        return render_template('success.html')
        
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return render_template(
            'error.html',
            error_title="Authentication Error",
            error_message="An error occurred while securely exchanging authentication tokens. Please try again."
        ), 500
