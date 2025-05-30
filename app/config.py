import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
# Load environment variables from .env file in the project root
load_dotenv(BASE_DIR / ".env")

class Settings:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
settings = Settings() 

print("SUPABASE_URL:", settings.SUPABASE_URL)
print("SUPABASE_SERVICE_KEY:", settings.SUPABASE_SERVICE_KEY)
print("OPENAI_API_KEY:", settings.OPENAI_API_KEY) 