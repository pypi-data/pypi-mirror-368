import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    create_access_keys_resp = client.kos.accessKeys.create_access_keys(
        key_name="enter key name",          
        region="enter the region",         
        x_region_id="enter the region id"    
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    
    
    
    print(f"Successfully created the Access Key: {create_access_keys_resp}")
    

except Exception as e:
    print(f"Error has occurred: {e}")

