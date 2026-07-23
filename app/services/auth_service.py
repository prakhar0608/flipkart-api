import os
import secrets
import requests
from urllib.parse import urlencode
from flask import session, current_app
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthService:
    """
    Service class handling authentication, state validation, token exchange,
    and token refresh with the Flipkart Ads API.
    """
    
    @staticmethod
    def generate_login_url() -> tuple[str, str]:
        """
        Generates a secure random state, stores it in the Flask session,
        and constructs the Flipkart OAuth authorization URL.
        
        Returns:
            tuple[str, str]: (authorization_url, state)
        """
        client_id = current_app.config.get('FLIPKART_CLIENT_ID')
        redirect_uri = current_app.config.get('FLIPKART_REDIRECT_URI')
        auth_base_url = current_app.config.get('FLIPKART_AUTHORIZATION_URL')
        
        if not client_id or not redirect_uri or not auth_base_url:
            logger.error("OAuth configuration missing: check FLIPKART_CLIENT_ID, FLIPKART_REDIRECT_URI, and FLIPKART_AUTHORIZATION_URL.")
            raise ValueError("OAuth configuration settings are incomplete.")
        
        state = secrets.token_urlsafe(32)
        session['oauth_state'] = state
        
        # Use official scopes specified in the ads agency documentation
        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'reporting campaign_management',
            'state': state
        }
        
        login_url = f"{auth_base_url}?{urlencode(params)}"
        logger.info("Successfully generated login URL and stored state in session.")
        return login_url, state

    @staticmethod
    def validate_state(returned_state: str) -> bool:
        """
        Compares the returned OAuth state parameter against the one stored in session.
        Clears the stored state upon execution to prevent replay attacks.
        
        Args:
            returned_state (str): The state parameter received in the callback request.
            
        Returns:
            bool: True if valid and matching, False otherwise.
        """
        stored_state = session.pop('oauth_state', None)
        
        if not stored_state:
            logger.warning("State validation failed: No state found in user session.")
            return False
            
        if not returned_state:
            logger.warning("State validation failed: No state parameter provided in request.")
            return False
            
        if not secrets.compare_digest(stored_state, returned_state):
            logger.warning("State validation failed: Returned state does not match session state.")
            return False
            
        logger.info("OAuth state parameter validated successfully.")
        return True

    @staticmethod
    def exchange_code_for_token(code: str) -> dict:
        """
        Exchanges the authorization code for an Access Token and a Refresh Token
        using parameters in the POST body.
        
        Args:
            code (str): The authorization code received from the callback.
            
        Returns:
            dict: The JSON response containing the access_token and refresh_token.
        """
        client_id = current_app.config.get('FLIPKART_CLIENT_ID')
        client_secret = current_app.config.get('FLIPKART_CLIENT_SECRET')
        redirect_uri = current_app.config.get('FLIPKART_REDIRECT_URI')
        token_url = current_app.config.get('FLIPKART_TOKEN_URL')
        
        if not client_id or not client_secret or not redirect_uri or not token_url:
            logger.error("Token exchange failed: OAuth credentials or endpoint not configured.")
            raise ValueError("OAuth credentials or endpoint configuration is incomplete.")
            
        logger.info("Initiating token exchange request with Flipkart Ads OAuth endpoint...")
        
        # Payload parameters sent directly in the POST body
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'scope': 'reporting campaign_management'
        }
        
        try:
            response = requests.post(
                token_url,
                data=payload,
                timeout=15
            )
            
            response.raise_for_status()
            token_data = response.json()
            logger.info("Successfully exchanged authorization code for tokens.")
            return token_data
            
        except requests.exceptions.Timeout as e:
            logger.error("Timeout occurred while exchanging code for token.")
            raise RuntimeError("Request timed out during token exchange.") from e
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network or HTTP error occurred during token exchange: {e}")
            raise RuntimeError("Failed to communicate with Flipkart OAuth token endpoint.") from e
            
        except ValueError as e:
            logger.error("Failed to parse token response as JSON.")
            raise RuntimeError("Received invalid response format from Flipkart token endpoint.") from e

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """
        Refreshes an expired access token using parameters in the POST body.
        
        Args:
            refresh_token (str): The refresh token.
            
        Returns:
            dict: The JSON response containing the new access_token and refresh_token.
        """
        client_id = current_app.config.get('FLIPKART_CLIENT_ID')
        client_secret = current_app.config.get('FLIPKART_CLIENT_SECRET')
        token_url = current_app.config.get('FLIPKART_TOKEN_URL')
        
        if not client_id or not client_secret or not token_url:
            logger.error("Token refresh failed: OAuth credentials or endpoint not configured.")
            raise ValueError("OAuth credentials or endpoint configuration is incomplete.")
            
        logger.info("Initiating token refresh request with Flipkart Ads OAuth endpoint...")
        
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(
                token_url,
                data=payload,
                timeout=15
            )
            
            response.raise_for_status()
            token_data = response.json()
            logger.info("Successfully refreshed access token.")
            return token_data
            
        except requests.exceptions.Timeout as e:
            logger.error("Timeout occurred while refreshing access token.")
            raise RuntimeError("Request timed out during token refresh.") from e
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network or HTTP error occurred during token refresh: {e}")
            raise RuntimeError("Failed to communicate with Flipkart OAuth token refresh endpoint.") from e
            
        except ValueError as e:
            logger.error("Failed to parse token refresh response as JSON.")
            raise RuntimeError("Received invalid response format from Flipkart token refresh endpoint.") from e
