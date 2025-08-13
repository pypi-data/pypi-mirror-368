from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    GetVPC_List_resp = client.highlvlvpc.list_vpcs(
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Successfully Executed {GetVPC_List_resp}")

except Exception as e:
    print(f"Error {e}")