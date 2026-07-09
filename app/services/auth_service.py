from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthService:
    """
    Service class handling authentication and authorization with Flipkart Ads API.
    """
    
    @staticmethod
    def process_authorization_code(code: str) -> bool:
        """
        Processes the OAuth authorization code returned from Flipkart.
        For now, this logs the code as per original functionality.
        
        Args:
            code (str): The authorization code from the query string parameters.
            
        Returns:
            bool: True if processed successfully, False otherwise.
        """
        # Print/log the code so it is visible in the server logs (Render console/local terminal)
        logger.info(f"Received OAuth code in AuthService: {code}")
        print(f"Received OAuth code: {code}") # Keep the exact print statement for log match compatibility
        
        # Future implementation of Flipkart Ads SDK login/token exchange will happen here.
        return True
