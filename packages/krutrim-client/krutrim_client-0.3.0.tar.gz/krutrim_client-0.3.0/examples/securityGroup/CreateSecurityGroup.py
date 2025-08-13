from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    create_security_group_resp = client.securityGroup.create_security_group(
        description =  "Security Group Description",
        name =  "Security Group Name",
        vpcid = "Enter the VCP ID",
        timeout = 1000,
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully created the Security Group:  {create_security_group_resp}")

except Exception as e:
    print(f"Error has occured: {e}")

