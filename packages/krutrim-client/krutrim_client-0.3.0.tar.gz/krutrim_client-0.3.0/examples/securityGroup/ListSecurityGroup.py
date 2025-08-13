from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    list_vpc_response = client.securityGroup.list_by_vpc(
        vpc_krn_identifier = "Enter the VPC ID under which you want to find the List of Security Group",
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Successfully fetched the Security Group List {list_vpc_response}")
except Exception as e:
    print(f"Exception has occured {e}")