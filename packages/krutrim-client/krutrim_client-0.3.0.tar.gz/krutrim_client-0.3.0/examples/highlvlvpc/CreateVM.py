from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)

try:
    create_vm_response  = client.highlvlvpc.create_instance(
        image_krn= "Enter the Image KRN",
        instanceName= "Enter the  VPC Name",
        instanceType= "Enter the instance type",
        # like CPU-1x-4GB
        network_id="Enter the Network ID",
        sshkey_name= "Enter the SSHkey Name/ if not you can create",
        subnet_id="Subnet ID",
        vm_volume_disk_size= "20",
        vpc_id="Enter the VPC ID",
        floating_ip= False,
        volume_size= 20,
        volume_name= "Enter the Volume Name",
        user_data = "",
        volumetype = "HNSS",
        qos = {},
        security_groups = ["Enter the security group ID"],
        tags = [],
        timeout = 6000,
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
        )   
    print(f"Created VM successfully:  {create_vm_response}")
except Exception as e:
    if "504" in str(e):
        print("VM creation request likely succeeded but timed out. Please check UI or use list API.")
    else:
        print(f"Exception occurred: {e}")
