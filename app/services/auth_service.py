import requests
from typing import Dict, Any
from flask import current_app
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthService:
    """
    Service class handling token exchange and token refresh with the Flipkart Ads API.
    
    SECURITY NOTE: 
    The initial OAuth authorization flow is now handled client-side by the official 
    Flipkart Login SDK. Backend state validation has been intentionally removed because 
    the official SDK does not expose a configurable custom state parameter in its 
    documented initialization to support CSRF validation on the callback.
    """

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """
        Exchanges the authorization code for an Access Token and a Refresh Token
        using parameters in the POST body.
        
        Args:
            code (str): The authorization code received from the callback.
            
        Returns:
            Dict[str, Any]: The JSON response containing the access_token and refresh_token.
            
        Raises:
            ValueError: If required configuration is missing or response is invalid.
            RuntimeError: If the HTTP request fails.
        """
        client_id = current_app.config.get('FLIPKART_CLIENT_ID')
        client_secret = current_app.config.get('FLIPKART_CLIENT_SECRET')
        redirect_uri = current_app.config.get('FLIPKART_REDIRECT_URI')
        token_url = current_app.config.get('FLIPKART_TOKEN_URL')
        
        if not all([client_id, client_secret, redirect_uri, token_url]):
            logger.error("Token exchange failed: OAuth credentials or endpoint not configured.")
            raise ValueError("OAuth credentials or endpoint configuration is incomplete.")
            
        logger.info("Initiating token exchange request with Flipkart Ads OAuth endpoint...")
        
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
            raise RuntimeError(f"Failed to communicate with Flipkart OAuth token endpoint: {e}") from e
            
        except ValueError as e:
            logger.error("Failed to parse token response as JSON.")
            raise RuntimeError("Received invalid response format from Flipkart token endpoint.") from e

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """
        Refreshes an expired access token using parameters in the POST body.
        
        Args:
            refresh_token (str): The refresh token.
            
        Returns:
            Dict[str, Any]: The JSON response containing the new access_token and refresh_token.
            
        Raises:
            ValueError: If required configuration is missing or response is invalid.
            RuntimeError: If the HTTP request fails.
        """
        client_id = current_app.config.get('FLIPKART_CLIENT_ID')
        client_secret = current_app.config.get('FLIPKART_CLIENT_SECRET')
        token_url = current_app.config.get('FLIPKART_TOKEN_URL')
        
        if not all([client_id, client_secret, token_url]):
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
            raise RuntimeError(f"Failed to communicate with Flipkart OAuth token refresh endpoint: {e}") from e
            
        except ValueError as e:
            logger.error("Failed to parse token refresh response as JSON.")
            raise RuntimeError("Received invalid response format from Flipkart token refresh endpoint.") from e

    @staticmethod
    def store_tokens(user_id: str, token_data: Dict[str, Any]) -> None:
        """
        Securely stores the access and refresh tokens.
        
        TODO: Currently uses Flask session as a temporary development storage.
        This MUST be updated to persist tokens in PostgreSQL (or another secure
        server-side datastore) keyed by the advertiser/user identity before production.
        
        Args:
            user_id (str): The unique identifier for the advertiser/user.
            token_data (Dict[str, Any]): The token payload containing access_token and refresh_token.
        """
        from flask import session
        logger.info(f"Storing tokens temporarily in session for user: {user_id}")
        
        # TODO: Replace the following session assignments with database insertions.
        # e.g., db.session.add(TokenModel(user_id=user_id, access_token=..., ...))
        session['access_token'] = token_data.get("access_token")
        session['refresh_token'] = token_data.get("refresh_token")
