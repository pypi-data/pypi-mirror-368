from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    get_instance_info_resp = client.highlvlvpc.retrieve_instance(
        krn = "Enter the Instance KRN",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Response Get Instance: {get_instance_info_resp}")
except Exception as e:
    print(f"Exception occured as e:  {e}")   