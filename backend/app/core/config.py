import os

# In a real application, get these from environment variables or a secrets manager.
# It's crucial that SECRET_KEY is kept secret and is a strong, random string.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "your-super-secret-key-for-dev-only-change-this"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
