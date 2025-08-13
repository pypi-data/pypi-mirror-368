from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    delete_volume_resp = client.kbs.delete_volume(
        k_tenant_id = "Enter the VPC ID",
        id = "Enter the Volume ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Volume Deleted Successfully")
except Exception as e:
    print(f"Exception has occured:  {e}")