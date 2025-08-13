from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try: 
    search_instance_resp = client.highlvlvpc.search_instances(
        vpc_id = "Enter the VPC ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Successfully searched for the instance:  {search_instance_resp}")
except Exception as e:
    print(f"Exception has occured: {e}")