from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    detach_security_group_rules_resp = client.securityGroup.detach_rule(
        ruleid ="Enter the Security Group Rule ID",
        securityid = "Enter the Security Group ID",
        vpcid = "Enter the VPC ID",
        x_region = "Enter the region",
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Rule detached successfully")
    delete_rule_resp = client.securityGroup.delete_rule(
        securitygroupruleid  = "Enter the rule ID",
        x_region = "Enter the region",
         # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )   

    print(f"Rule deleted successfully")
except Exception as e:
    print(f"Exception has occurred:  {e}")