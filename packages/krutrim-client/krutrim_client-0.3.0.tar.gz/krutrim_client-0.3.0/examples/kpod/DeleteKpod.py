import os
import json
from dotenv import load_dotenv
from krutrim_client import KrutrimClient


load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    kpod_krn = "enter the pod krn"

    if kpod_krn:
        delete_pod_resp = client.kpod.pod.delete(kpod_krn)
        print(f"Pod with ID {kpod_krn} has been deleted successfully.")
    else:
        print(f"Pod with ID {kpod_krn} not found.")
except Exception as e:
    print(f"Error occurred: {e}")
