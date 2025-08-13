from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    get_sshkey_response = client.sshkey.retrieve_sshkey(
        ssh_key_identifier = "0070140197",
        x_region = "In-Bangalore-1"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully retrieve the SSH Key List {get_sshkey_response}!")
except Exception as e:
    print(f"Exception! {e}")