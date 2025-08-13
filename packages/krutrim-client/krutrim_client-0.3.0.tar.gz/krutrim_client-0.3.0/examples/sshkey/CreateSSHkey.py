from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    create_sshkey_response = client.sshkey.create_sshkey(
        key_name = "Enter the Key Name",
        public_key = "Enter the Public key",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully Created the SSHKEY {create_sshkey_response}")
except Exception as e:
    print(f"Exception occured {e}")