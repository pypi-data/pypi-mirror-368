from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    create_image_response = client.highlvlvpc.create_image(
        name="enter the name", 
        instance_krn="enter the instance krn",  
        x_region="enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"  
       
    )

    print(f"Successfully created the image: {create_image_response}")

except Exception as e:
    print(f"Exception: {e}")
