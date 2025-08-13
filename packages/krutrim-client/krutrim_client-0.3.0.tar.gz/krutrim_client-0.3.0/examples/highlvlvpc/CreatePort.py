from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    create_port_response = client.highlvlvpc.create_port(
        floating_ip = False,
        name = "Enter the Port Name",
        network_id = "Enter the Network ID",
        subnet_id =  "Enter the Subnet ID",
        vpc_id = "Enter the VPC ID",
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully created the port:  {create_port_response}")
except Exception as e:
    print(f"Exception has occurred:  {e}")