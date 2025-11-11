from storage3 import create_client
from config import settings

url = settings.SUPABASE_URL
key = settings.SUPABASE_SERVICE_KEY

headers = {
    "apiKey": key,
    "Authorization": f"Bearer {key}"

}

storage_client = create_client(url=url, headers=headers, is_async=False)