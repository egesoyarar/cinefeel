import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
MOVIES_PER_PAGE = 10