from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    delete_sshkey_resp = client.sshkey.delete_sshkey(
        ssh_key_identifier = "Enter the uuid associated to your ssh key which you want to delete",
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print("Successfully deleted the SSH Key")

except Exception as e:
    print(f"Exception has occured {e}")