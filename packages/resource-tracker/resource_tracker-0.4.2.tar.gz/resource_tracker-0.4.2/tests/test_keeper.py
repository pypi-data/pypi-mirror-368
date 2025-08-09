from resource_tracker.keeper import (
    get_instance_price,
    get_recommended_cloud_servers,
    keeper_request,
)


def test_keeper_request():
    """Test Keeper API requests."""
    assert keeper_request("/healthcheck") is not None
    assert get_instance_price("aws", "us-east-1", "t3.micro") is not None
    assert get_recommended_cloud_servers(1, 1024, n=1) is not None
    servers = get_recommended_cloud_servers(1, 1000, n=1)
    assert len(servers) == 1
    assert servers[0]["vcpus"] == 1
    assert servers[0]["memory_amount"] == 1024
    assert servers[0]["gpu_count"] == 0
