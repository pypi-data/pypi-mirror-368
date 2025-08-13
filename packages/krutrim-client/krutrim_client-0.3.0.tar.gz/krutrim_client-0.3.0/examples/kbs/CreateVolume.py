from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    create_volume_resp = client.kbs.create_volume(
        availability_zone = "nova",
        multiattach = True,
        name = "Enter the Volume Name",
        size = 20,
        volumetype = "HNSS",
        k_tenant_id = "Enter the VPC ID",
        description = "Enter the Description",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Created the Volume: {create_volume_resp}")
except Exception as e:
    print(f"Exception has occured:  {e}")




