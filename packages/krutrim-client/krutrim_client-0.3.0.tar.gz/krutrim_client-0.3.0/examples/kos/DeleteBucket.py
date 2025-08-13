import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    delete_response = client.kos.buckets.delete_bucket(
        bucket_krn="enter the bucket krn",
        x_region_id="enter the region" 
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"               
    )

    print(f"Bucket deleted successfully: {delete_response}")

except Exception as e:
    print(f"Error has occurred: {e}")
