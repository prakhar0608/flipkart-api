import uuid
from app.extensions import db

def generate_uuid():
    """Generates a standard UUID4 representation."""
    return uuid.uuid4()
