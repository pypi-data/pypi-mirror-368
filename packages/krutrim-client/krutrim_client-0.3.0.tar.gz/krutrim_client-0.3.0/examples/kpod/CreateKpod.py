import os
from dotenv import load_dotenv
from krutrim_client import KrutrimClient

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

# Create a client instance
client = KrutrimClient(api_key=api_key)

try:
    # Create a new pod with the specified parameters
    pod_resp = client.kpod.pod.create(
        container_disk_size="enter disk size",                             
        expose_http_ports="enter http ports",                             
        expose_tcp_ports="enter tcp ports",                               
        flavor_name="enter flavour name",                
        has_encrypt_volume=True,                              
        has_jupyter_notebook=bool,                 #enter eg. true or false           
        has_ssh_access=bool,                        #enter eg. true or false          
        pod_name="enter pod name",                                      
        environment_variables=[                              
            {"name": "VAR_NAME", "value": "VALUE"}
        ],
        pod_template_id=1,                                    
        region="enter region", 
        # x_region possible values "In-Bangalore-1"                             
        sshkey_name="enter sshkeyname",                           
        volume_disk_size="enter volumedisk size",                                  
        volume_mount_path="enter volume mount path",                      
    )

    print(f"Pod created successfully.\nResponse:\n{pod_resp}")

except Exception as e:
    print("Error creating pod:")
    print(e)

    

    





