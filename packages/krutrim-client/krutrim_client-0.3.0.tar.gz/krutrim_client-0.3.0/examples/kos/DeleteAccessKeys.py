import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    
    delete_access_keys_resp = client.kos.accessKeys.delete_access_keys(
        access_key_id = "enter the access_key_id",
        x_region_id="enter the region_id",  
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    
    ) 
    print(f"Successfully deleted access key: {delete_access_keys_resp}")


except Exception as e:
    print(f"Error has occurred: {e}")
