import os
from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

# 1. Root route for health check and basic verification
@app.route('/')
def home():
    """
    Returns a simple message to indicate the app is running.
    Useful for checking deployment status.
    """
    return "App is running"

# 2. Callback route to handle the OAuth redirect
@app.route('/callback')
def callback():
    """
    Handles the redirect from Flipkart Ads API after successful authentication.
    Extracts the authorization 'code' from the query parameters.
    """
    # Extract the "code" parameter from the query string
    # E.g., /callback?code=YOUR_AUTHORIZATION_CODE
    code = request.args.get('code')
    
    # Print the code to the server logs
    # You can view this in Render's log viewer
    print(f"Received OAuth code: {code}")
    
    # Return the code in the HTTP response
    if code:
        return jsonify({
            "message": "OAuth code received successfully", 
            "code": code
        })
    else:
        return jsonify({
            "message": "Authorization failed or no code provided", 
            "error": "Missing code parameter"
        }), 400

# 3. Production-ready execution block
if __name__ == '__main__':
    # Retrieve the PORT from the environment variables (Render sets this automatically)
    # Default to 5000 if not running on a cloud provider
    port = int(os.environ.get('PORT', 5000))
    
    # Use host="0.0.0.0" so the server binds to all public IPs, 
    # making it accessible from outside the container/server
    app.run(host='0.0.0.0', port=port)
