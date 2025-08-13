from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key = api_key)

try: 
    delete_image_resp = client.highlvlvpc.delete_image(
        snapshot_krn = "enter the snapshot_krn",
        
    )

    print(f"Successfully delete for the snapshot_krn")
except Exception as e:
    print(f"Exception has occured: {e}")