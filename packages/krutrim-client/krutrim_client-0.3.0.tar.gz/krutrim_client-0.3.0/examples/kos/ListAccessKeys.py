import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient


load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    list_access_keys_resp = client.kos.accessKeys.list(
        
    )

    print(f"Access Keys List: {list_access_keys_resp}")

except Exception as e:
    print(f"Error has occurred: {e}")

