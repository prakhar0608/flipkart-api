import os
from app import create_app

# Expose app for WSGI / Gunicorn (matches 'web: gunicorn app:app' in Procfile)
app = create_app()

if __name__ == '__main__':
    # Retrieve the PORT from the environment variables (Render sets this automatically)
    # Default to 5000 if not running on a cloud provider
    port = int(os.environ.get('PORT', 5000))
    
    # Use host="0.0.0.0" so the server binds to all public IPs, 
    # making it accessible from outside the container/server
    app.run(host='0.0.0.0', port=port)
