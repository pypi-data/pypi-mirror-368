import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient


load_dotenv()
api_key = os.getenv("API_KEY")
client = KrutrimClient(api_key=api_key)

try:
    
    kpod_krn = "enter the pod krn"  
    action = "enter start or stop"  
    
    pod = client.kpod.pod.update(kpod_krn=kpod_krn, action=action)
    print(f"Pod with ID {kpod_krn} has been {action}ed successfully.")
    
except Exception as e:
    print(f"Error performing the action: {e}")
