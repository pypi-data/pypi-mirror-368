from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)



try:
    highlvlvpc_delete_vpc_response = client.highlvlvpc.delete_vpc(
        vpc_id="Enter the VPC ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Deleted the VPC successfully")
except Exception as e:
    print(f"Exception:  {e}")    