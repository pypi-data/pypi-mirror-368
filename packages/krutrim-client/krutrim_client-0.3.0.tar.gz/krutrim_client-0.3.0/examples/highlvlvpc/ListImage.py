from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key = api_key)

try: 
    list_image_resp = client.highlvlvpc.list_image(
        region_id = "enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Successfully searched for the instance:  {list_image_resp}")
except Exception as e:
    print(f"Exception has occured: {e}")