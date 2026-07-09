from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/callback')
def callback():
    """
    Handles the redirect from Flipkart Ads API after successful authentication.
    Extracts the authorization 'code' from the query parameters.
    """
    # Extract the "code" parameter from the query string
    code = request.args.get('code')
    
    # Return the code in the HTTP response
    if code:
        AuthService.process_authorization_code(code)
        return jsonify({
            "message": "OAuth code received successfully", 
            "code": code
        })
    else:
        return jsonify({
            "message": "Authorization failed or no code provided", 
            "error": "Missing code parameter"
        }), 400
