from json import loads
from typing import Dict, List, Optional
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen


def keeper_request(
    path: str, timeout: int = 2, endpoint: str = "https://keeper.sparecores.net"
) -> Optional[dict]:
    """Fetch data from a SC Keeper URL with a custom header.

    Args:
        path: The path to fetch data from.
        timeout: The timeout for the request.
        endpoint: The endpoint to fetch data from.

    Returns:
        The JSON-decoded response data, or None if an error occurs.
    """
    try:
        request = Request(urljoin(endpoint, path))
        request.add_header("X-Application-ID", "resource-tracker")
        with urlopen(request, timeout=timeout) as response:
            return loads(response.read().decode("utf-8"))
    except Exception:
        return None


def get_instance_price(vendor_id, region_id, instance_type) -> Optional[float]:
    """Get the on-demand price for a specific instance type in a region.

    Args:
        vendor_id: The ID of the vendor (e.g. "aws", "azure", "gcp")
        region_id: The ID of the region (e.g. "us-east-1", "us-west-2")
        instance_type: The type of instance (e.g. "t3.micro", "m5.large")

    Returns:
        The on-demand price for the instance type in the region, or None if no price is found.
    """
    try:
        pricing_data = keeper_request(f"/server/{vendor_id}/{instance_type}/prices")

        for item in pricing_data:
            if (
                item.get("region_id") == region_id
                and item.get("allocation") == "ondemand"
                and item.get("operating_system") == "Linux"
            ):
                return item.get("price")

        # fallback to the first on-demand price in other regions
        for item in pricing_data:
            if (
                item.get("allocation") == "ondemand"
                and item.get("operating_system") == "Linux"
            ):
                return item.get("price")

        return None
    except Exception:
        return None


def get_recommended_cloud_servers(
    cpu: int,
    memory: int,
    gpu: Optional[int] = None,
    vram: Optional[int] = None,
    n: int = 10,
) -> List[Dict]:
    """Get the cheapest cloud servers for the given resources from Spare Cores.

    Args:
        cpu: The minimum number of vCPUs.
        memory: The minimum amount of memory in MB.
        gpu: The minimum number of GPUs.
        vram: The minimum amount of VRAM in GB.
        n: The number of recommended servers to return.

    Returns:
        A list of recommended server configurations ordered by price.

    References:
        - https://sparecores.com/servers
    """
    try:
        params = {
            "vcpus_min": cpu,
            "memory_min": round(memory / 1024),  # convert MiB to GiB
            "order_by": "min_price_ondemand",
            "order_dir": "asc",
            "limit": n,
        }
        if gpu and gpu > 0:
            params["gpu_min"] = gpu
        if vram and vram > 0:
            params["gpu_memory_total"] = vram
        return keeper_request(f"/servers?{urlencode(params)}")
    except Exception:
        return []
