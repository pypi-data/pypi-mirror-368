from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try: 
    Get_Vpc_task_status_resp = client.highlvlvpc.get_vpc_task_status(
        task_id = "Enter the Task ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )

    print(f"Get VPC task status executed successfully : {Get_Vpc_task_status_resp}")

except Exception as e:
    print(f"Exception  {e}")    