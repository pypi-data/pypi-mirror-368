

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from krutrim_client import KrutrimClient, AsyncKrutrimClient
from krutrim_client.types import (
    ImageList,
    VpcDetail,
    PortDetail,
    InstanceInfo,
    SuccessResponse,
    InstanceInfoList,
    HighlvlvpcListVpcsResponse,
    HighlvlvpcSearchVpcsResponse,
    HighlvlvpcSearchPortsResponse,
    HighlvlvpcSearchNetworksResponse,
    HighlvlvpcListSubnetConnectionsResponse,
)
from krutrim_client._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestHighlvlvpc:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    
    @pytest.mark.skip()
    @parametrize
    def test_method_create_instance(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_instance_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            floating_ip=False,
            security_group_rules_name="ingress",
            security_group_rules_port="22",
            security_group_rules_protocol="tcp",
            user_data="IyEvYmluL2Jhc2gKdXNlcmFkZCAtbSAtcyAvYmluL2Jhc2gga3J1dHJpbQplY2hvICJrcnV0cmltOnBhc3N3b3JkIiB8IGNocGFzc3dkCnRvdWNoIC90bXAvc2FtcGxlLnR4dAo=",
            volume_name="volume_test_instance_vpc_06",
            volume_size="5",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_instance(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_instance(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_port(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(PortDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_port(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(PortDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_port(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(PortDetail, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_subnet(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    def test_method_create_subnet_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
                "description": "Subnet for application servers",
                "gateway_ip": "10.0.1.1",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_subnet(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_subnet(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert highlvlvpc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_create_vpc(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_create_vpc_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            network={
                "admin_state_up": True,
                "name": "name",
            },
            security_group={
                "description": "description",
                "name": "name",
            },
            security_group_rule={
                "direction": "ingress",
                "ethertypes": "IPv4",
                "port_max_range": 0,
                "port_min_range": 0,
                "protocol": "protocol",
                "remote_ip_prefix": "remoteIPPrefix",
            },
            subnet={
                "cidr": "cidr",
                "description": "description",
                "gateway_ip": "192.168.1.1",
                "ip_version": 4,
                "name": "name",
                "egress": True,
                "ingress": True,
            },
            vpc={
                "description": "description",
                "enabled": True,
                "name": "name",
            },
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_create_vpc(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_create_vpc(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_instance(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_instance_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            instance_krn="krn:vm:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:instance:b7830594-6e28-4d81-893d-e48cb6b02e49",
            instance_name="my-instance-dec-17-1",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete_instance(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete_instance(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete_vpc(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete_vpc(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete_vpc(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert highlvlvpc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_get_vpc_task_status(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_vpc_task_status(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_vpc_task_status(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

   
    @pytest.mark.skip()
    @parametrize
    def test_method_list_instance_info(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_instance_info_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            page=1,
            page_size=1,
            vpc_id="vpc_id",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_instance_info(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_instance_info(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_subnet_connections(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_subnet_connections(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_subnet_connections(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_vpcs(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_vpcs(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_vpcs(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_instance(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_instance(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_instance(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_vpc(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_retrieve_vpc_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            vpc_id="krn:vpc:Colo1-qa:5373689502:46208820-5e16-4dac-b110-e6de4889d50a:vpc:952a6224-ed83-4870-9226-c8f97ac25b8e",
            vpc_name="HL_VPC_Dec_4",
        )
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_retrieve_vpc(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_retrieve_vpc(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search_instances(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_instances_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
            limit=1,
            page=1,
            ip_fixed="20.169.1.5",
            ip_floating="100.20.30.40",
            krn="krn:vm:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:instance:d84de151-9086-4c66-aa3b-cb615fc1d747",
            name="vm_jan_3_exp-1",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search_instances(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search_instances(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search_networks(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search_networks(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search_networks(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search_ports(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_ports(
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_ports_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_ports(
            x_account_id="acc-1234567890",
            name="name",
            network_id="network_id",
            page=1,
            port_id="port_id",
            size=1,
            status="status",
            vpc_id="vpc_id",
        )
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search_ports(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.search_ports(
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search_ports(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.search_ports(
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_search_vpcs(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_vpcs()
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_search_vpcs_with_all_params(self, client: KrutrimClient) -> None:
        highlvlvpc = client.highlvlvpc.search_vpcs(
            name="name",
            page=1,
            size=1,
            status="status",
        )
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_search_vpcs(self, client: KrutrimClient) -> None:
        response = client.highlvlvpc.with_raw_response.search_vpcs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = response.parse()
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_search_vpcs(self, client: KrutrimClient) -> None:
        with client.highlvlvpc.with_streaming_response.search_vpcs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = response.parse()
            assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncHighlvlvpc:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])



    @pytest.mark.skip()
    @parametrize
    async def test_method_create_instance(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_instance_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            floating_ip=False,
            security_group_rules_name="ingress",
            security_group_rules_port="22",
            security_group_rules_protocol="tcp",
            user_data="IyEvYmluL2Jhc2gKdXNlcmFkZCAtbSAtcyAvYmluL2Jhc2gga3J1dHJpbQplY2hvICJrcnV0cmltOnBhc3N3b3JkIiB8IGNocGFzc3dkCnRvdWNoIC90bXAvc2FtcGxlLnR4dAo=",
            volume_name="volume_test_instance_vpc_06",
            volume_size="5",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_instance(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_instance(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.create_instance(
            image_krn="krn:vm:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:image:89132209-ad64-4a2b-8d06-85d0b83b8817",
            instance_name="test_instance_surya_1_19nov",
            instance_type="CPU-1x-4GB",
            network_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:network:dfc60763-6174-43d5-8b07-55b81d10aeba",
            region="in-hyd-1",
            security_groups=[
                "krn:krutrim-sg:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:sg:c88dd669-612a-4829-afc7-453aabac6eb6"
            ],
            sshkey_name="bhaskara",
            subnet_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:subnet:f61d540c-a82d-4959-bd70-3a00b6bfcfb2",
            vm_volume_disk_size="10",
            vpc_id="krn:vpc:Colo2-perf:1587599074:c094d34c-b137-4635-b020-3b733375dd89:vpc:323fc1d4-8b0a-4f26-9406-42a2732d65f5",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_port(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(PortDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_port(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(PortDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_port(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.create_port(
            floating_ip=False,
            name="vm_jan_3_exp-1_port",
            network_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:network:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            subnet_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:subnet:yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy",
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(PortDetail, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_subnet(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_subnet_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
                "description": "Subnet for application servers",
                "gateway_ip": "10.0.1.1",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_subnet(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_subnet(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.create_subnet(
            subnet_data={
                "cidr": "10.0.1.0/24",
                "ip_version": 4,
                "name": "my-app-subnet",
            },
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert highlvlvpc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_vpc(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_create_vpc_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            network={
                "admin_state_up": True,
                "name": "name",
            },
            security_group={
                "description": "description",
                "name": "name",
            },
            security_group_rule={
                "direction": "ingress",
                "ethertypes": "IPv4",
                "port_max_range": 0,
                "port_min_range": 0,
                "protocol": "protocol",
                "remote_ip_prefix": "remoteIPPrefix",
            },
            subnet={
                "cidr": "cidr",
                "description": "description",
                "gateway_ip": "192.168.1.1",
                "ip_version": 4,
                "name": "name",
                "egress": True,
                "ingress": True,
            },
            vpc={
                "description": "description",
                "enabled": True,
                "name": "name",
            },
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_create_vpc(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_create_vpc(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.create_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_instance(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_instance_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            instance_krn="krn:vm:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:instance:b7830594-6e28-4d81-893d-e48cb6b02e49",
            instance_name="my-instance-dec-17-1",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete_instance(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete_instance(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.delete_instance(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete_vpc(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete_vpc(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert highlvlvpc is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete_vpc(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.delete_vpc(
            vpc_id="vpc_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert highlvlvpc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_vpc_task_status(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_vpc_task_status(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_vpc_task_status(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.get_vpc_task_status(
            task_id="task_id",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(SuccessResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

   

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_instance_info(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_instance_info_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            page=1,
            page_size=1,
            vpc_id="vpc_id",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_instance_info(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_instance_info(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.list_instance_info(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_subnet_connections(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_subnet_connections(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_subnet_connections(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.list_subnet_connections(
            vpc_id="krn:vpc:colo-2-acceptance:9550999532:cbcf451f-f15d-40e1-af39-4242e727732c:vpc:e0408184-6593-4aaa-a607-ca6e76afe30e",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(HighlvlvpcListSubnetConnectionsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.list_vpcs(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(HighlvlvpcListVpcsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_instance(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_instance(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_instance(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.retrieve_instance(
            krn="krn",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(InstanceInfo, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_vpc(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_retrieve_vpc_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            vpc_id="krn:vpc:Colo1-qa:5373689502:46208820-5e16-4dac-b110-e6de4889d50a:vpc:952a6224-ed83-4870-9226-c8f97ac25b8e",
            vpc_name="HL_VPC_Dec_4",
        )
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_retrieve_vpc(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_retrieve_vpc(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.retrieve_vpc(
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(VpcDetail, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    
    @pytest.mark.skip()
    @parametrize
    async def test_method_search_instances(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_instances_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
            limit=1,
            page=1,
            ip_fixed="20.169.1.5",
            ip_floating="100.20.30.40",
            krn="krn:vm:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:instance:d84de151-9086-4c66-aa3b-cb615fc1d747",
            name="vm_jan_3_exp-1",
        )
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search_instances(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search_instances(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.search_instances(
            vpc_id="krn:vpc:Colo1-qa:0005604999:718a1c1c-55db-47c7-8b01-bd5f44d8e076:vpc:d5e2c968-9db4-4c05-99fc-293107c33f3e",
            k_customer_id="k-customer-id",
            x_account_id="acc-1234567890",
            x_user_email="dev@stainless.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(InstanceInfoList, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_networks(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search_networks(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search_networks(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.search_networks(
            vpc_id="vpc_id",
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(HighlvlvpcSearchNetworksResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_ports(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_ports(
            x_account_id="acc-1234567890",
        )
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_ports_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_ports(
            x_account_id="acc-1234567890",
            name="name",
            network_id="network_id",
            page=1,
            port_id="port_id",
            size=1,
            status="status",
            vpc_id="vpc_id",
        )
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search_ports(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.search_ports(
            x_account_id="acc-1234567890",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search_ports(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.search_ports(
            x_account_id="acc-1234567890",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(HighlvlvpcSearchPortsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_vpcs()
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_search_vpcs_with_all_params(self, async_client: AsyncKrutrimClient) -> None:
        highlvlvpc = await async_client.highlvlvpc.search_vpcs(
            name="name",
            page=1,
            size=1,
            status="status",
        )
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_search_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        response = await async_client.highlvlvpc.with_raw_response.search_vpcs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        highlvlvpc = await response.parse()
        assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_search_vpcs(self, async_client: AsyncKrutrimClient) -> None:
        async with async_client.highlvlvpc.with_streaming_response.search_vpcs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            highlvlvpc = await response.parse()
            assert_matches_type(HighlvlvpcSearchVpcsResponse, highlvlvpc, path=["response"])

        assert cast(Any, response.is_closed) is True
