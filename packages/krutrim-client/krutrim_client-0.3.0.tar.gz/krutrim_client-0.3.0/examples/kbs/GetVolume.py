from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try: 
    get_volume_response = client.kbs.retrieve_volume(
        volume_id = "Enter the Volume ID",
        k_tenant_id = "Enter the VPC ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Get Volume Response:  {get_volume_response}")
except Exception as e:
    print(f"Exception has occured:  {e}")