from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    Create_Subnet_Response = client.highlvlvpc.create_subnet(

        subnet_data = {
        "cidr": "10.0.39.0/25",
        "gateway_ip": "10.0.39.1",
        "name": "Enter the Subnet Name",
        "description": "Enter the subnet description",
        "ip_version": 4,
        "ingress": False,
        "egress": False
    },
    vpc_id = "Enter the VPC ID",
    router_krn = "Enter the Router ID",
    timeout = 1000,
    x_region = "Enter the region"
    # x_region possible values "In-Bangalore-1","In-Hyderabad-1"

    )
    print(f"Successfully created the Subnet")

except Exception as e:
    print(f"Exception: {e}")       