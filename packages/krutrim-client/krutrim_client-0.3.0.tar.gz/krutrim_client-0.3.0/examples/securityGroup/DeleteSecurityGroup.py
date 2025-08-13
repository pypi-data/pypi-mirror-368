from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try: 
    delete_security_group_resp = client.securityGroup.delete_security_group(
        securitygroupid = "Enter the Secuiry Group ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Deleted Successfully")
except Exception as e:
    print(f"Error has occured:  {e}")