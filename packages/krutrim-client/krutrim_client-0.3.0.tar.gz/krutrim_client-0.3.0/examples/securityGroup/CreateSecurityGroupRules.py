from krutrim_client import KrutrimClient
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("api_key")

client = KrutrimClient(api_key = api_key)


try:
    create_security_group_rules_resp = client.securityGroup.create_rule(
        direction= "ingress",
        ethertypes = "ipv4",
        port_max_range = 222,
        port_min_range =100,
        protocol = "TCP",
        remote_ip_prefix = "192.168.0.1/24",
        vpcid = "Enter the VPC ID",
        timeout = 1000,
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Security Group Rules created successfully:{create_security_group_rules_resp}")

    securtiy_group_rule_id  = create_security_group_rules_resp.result['id']

    attach_security_group_rule_resp = client.securityGroup.attach_rule(
        ruleid = securtiy_group_rule_id,
        securityid = "Enter the security group ID",
        vpcid = "Enter the VCP ID",
        x_region = "Enter the region"
        # x_region possible values "In-Bangalore-1","In-Hyderabad-1"
    )
    print(f"Successfully attched the security group rules:  {attach_security_group_rule_resp}")
except Exception as e:
    print(f"Error has occured: {e}")