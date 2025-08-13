from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    get_instance_info_list_resp = client.highlvlvpc.list_instance_info(
        vpc_id = "Enter the VPC ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully fetched the details {get_instance_info_list_resp}")
except Exception as e:
    print(f"Exception as occurred {e}")