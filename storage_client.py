from supabase import create_client, Client
from config import settings

url = settings.SUPABASE_URL
key = settings.SUPABASE_SERVICE_KEY

supabase_client: Client = create_client(url, key)