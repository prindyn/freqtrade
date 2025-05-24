import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# In a real application, get these from environment variables or a secrets manager.
# It's crucial that SECRET_KEY is kept secret and is a strong, random string.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "your-super-secret-key-for-dev-only-change-this"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database configuration - Default to PostgreSQL for development
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/freqtrade_saas"
)

# Debug mode
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
