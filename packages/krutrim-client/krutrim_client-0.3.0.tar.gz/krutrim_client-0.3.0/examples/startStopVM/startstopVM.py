from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    start_stop_VM_resp = client.startStopVM.perform_action(
        instance_krn = "Enter the VM ID",
        x_region = "Enter the region",
        action = "Enter the action start/stop",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
        timeout = 50000,
    )

    print(f"Success!")

except Exception as e:
    print(f"Exception has occured {e}")