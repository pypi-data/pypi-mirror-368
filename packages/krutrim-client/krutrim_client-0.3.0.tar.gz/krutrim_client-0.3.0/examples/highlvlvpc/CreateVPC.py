from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    Create_VPC_resp = client.highlvlvpc.create_vpc(
         network={
            "name": "Enter the Network Name",
            "admin_state_up": True,
        },
        security_group={
            "name": "Enter the Security Group Name",
            "description": "Enter the Securiy group description",
        },
        security_group_rule={
            "direction": "ingress",
            "ethertypes": "IPv4",
            "protocol": "TCP",
            "portMinRange": 22,
            "portMaxRange": 22,
            "remoteIPPrefix": "0.0.0.0/0"
            },
        
        subnet={
            "cidr": "10.0.38.0/25",
            "gateway_ip": "10.0.38.2",
            "name": "Enter the Subnet Name",
            "description": "Enter the Subnet Description",
            "ip_version": 4,
            "ingress": False,
            "egress": False,
        },
        vpc={
            "name": "Enter the VPC Name",
            "description": "Enter the VPC Description",
            "enabled": True,
        },
        x_region = "Enter the region",
        timeout = 60000
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully created the VPC:  {Create_VPC_resp}")

except Exception as e:
    print(f"Exception occured in creating the VPC:  {e}")