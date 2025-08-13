import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient


load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    create_bucket_resp = client.kos.buckets.create_bucket(
        name="enter the bucket name",  
        region="enter the region",     
        x_region_id="enter the region" 
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    
    print(f"successfully created bucket: {create_bucket_resp}")

except Exception as e:
    print(f"Error has occurred: {e}")

